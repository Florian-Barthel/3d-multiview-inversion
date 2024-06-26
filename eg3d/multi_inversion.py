""" Projecting input images into latent spaces. """
import json
import os
import time
from time import perf_counter
from typing import List
import click
import imageio
import numpy as np
import PIL.Image
import torch
import pickle
from torch.utils.tensorboard import SummaryWriter

import dnnlib
import legacy
from inversion.w_inversion import project
from inversion.pti_inversion import project_pti
from inversion.load_data import ImageItem, load
from inversion.image_selection import select_evenly



@click.command()
@click.option('--network', 'network_pkl', help='Network pickle filename', required=True)
@click.option('--target', 'target_fname', help='Target image file to project to', required=True, metavar='FILE|DIR')
@click.option('--num-steps', help='Number of optimization steps', type=int, default=500, show_default=True)
@click.option('--num-steps-pti', help='Number of optimization steps for pivot tuning', type=int, default=350,
              show_default=True)
@click.option('--seed', help='Random seed', type=int, default=303, show_default=True)
@click.option('--save-video', help='Save an mp4 video of optimization progress', type=bool, default=False,
              show_default=True)
@click.option('--outdir', help='Where to save the output images', required=True, metavar='DIR')
@click.option('--fps', help='Frames per second of final video', default=30, show_default=True)
@click.option('--num-targets', help='Number of targets to use for inversion', default=10, show_default=True)
@click.option('--downsampling', help='Downsample images from 512 to 256', type=bool, required=True)
@click.option('--optimize-cam', type=bool, required=True)
def run_projection(
        network_pkl: str,
        target_fname: str,
        outdir: str,
        save_video: bool,
        seed: int,
        num_steps: int,
        num_steps_pti: int,
        fps: int,
        num_targets: int,
        downsampling: bool,
        optimize_cam: bool
):
    cur_time = time.strftime("%Y%m%d-%H%M", time.localtime())
    desc = ("/" + cur_time)
    desc += f"_multiview_{num_targets}"
    desc += f"_iter_{num_steps}_{num_steps_pti}"
    data_index = target_fname.split("/")[-1]
    desc += f"_data_{data_index}"
    os.makedirs(outdir, exist_ok=True)
    outdir += desc
    writer = SummaryWriter(outdir)

    np.random.seed(seed)
    torch.manual_seed(seed)

    # Load networks.
    print('Loading networks from "%s"...' % network_pkl)
    device = torch.device('cuda')
    with dnnlib.util.open_url(network_pkl) as fp:
        network_data = legacy.load_network_pkl(fp)
        G = network_data['G_ema'].requires_grad_(False).to(device)  # type: ignore

    G.rendering_kwargs["ray_start"] = 2.35

    images: List[ImageItem] = load(target_fname, img_resolution=G.img_resolution, device=device)

    start_time = perf_counter()
    target_indices = select_evenly(images, num_targets)

    projected_w_steps = project(
        G,
        images=images,
        num_steps=num_steps,
        device=device,
        outdir=outdir,
        target_indices=target_indices,
        writer=writer,
        downsampling=downsampling,
        optimize_cam=optimize_cam,
        w_plus=True
    )
    time_project_w = perf_counter() - start_time

    start_time = perf_counter()
    G_steps = project_pti(
        G,
        images=images,
        w_pivot=projected_w_steps[-1:],
        num_steps=num_steps_pti,
        device=device,
        outdir=outdir,
        target_indices=target_indices,
        writer=writer,
        downsampling=downsampling
    )
    time_pti = perf_counter() - start_time
    with open(outdir + "/config.json", "w") as file:
        json.dump({
            "net": network_pkl,
            "target_fname": target_fname,
            "seed": seed,
            "num_steps": num_steps,
            "num_steps_pti": num_steps_pti,
            "num_targets": num_targets,
            "downsampling": downsampling,
            "optimize_cam": optimize_cam,
            "time": cur_time,
            "time_project_w": time_project_w,
            "time_pti": time_pti
        }, file)

    # Save final projected frame and W vector.
    images[0].target_pil.save(f'{outdir}/target.png')
    projected_w = projected_w_steps[-1]
    G_final = G_steps[-1].to(device)
    synth_image = G_final.synthesis(projected_w.unsqueeze(0).to(device), c=images[0].c_item.c, noise_mode='const')[
        'image']
    synth_image = (synth_image + 1) * (255 / 2)
    synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
    PIL.Image.fromarray(synth_image, 'RGB').save(f'{outdir}/proj.png')
    np.savez(f'{outdir}/projected_w.npz', w=projected_w.unsqueeze(0).cpu().numpy())

    with open(f'{outdir}/fintuned_generator.pkl', 'wb') as f:
        network_data["G_ema"] = G_final.eval().requires_grad_(False).cpu()
        pickle.dump(network_data, f)

    # Render debug output: optional video and projected image and W vector.
    if save_video:
        target_indices = select_evenly(images, 5)
        video = imageio.get_writer(f'{outdir}/proj.mp4', mode='I', fps=fps, codec='libx264', bitrate='16M')
        print(f'Saving optimization progress video "{outdir}/proj.mp4"')
        for projected_w in projected_w_steps[::]:
            views = []
            for i, target_index in enumerate(target_indices):
                cam_i = images[target_index].c_item.c
                synth_image = G.synthesis(projected_w.unsqueeze(0).to(device), c=cam_i, noise_mode='const')['image']
                synth_image = (synth_image + 1) * (255 / 2)
                synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
                views.append(np.concatenate([images[target_index].t_uint8, synth_image], axis=0))
            video.append_data(np.concatenate(views, axis=1))
        for G_new in G_steps:
            G_new.to(device)
            views = []
            for i, target_index in enumerate(target_indices):
                cam_i = images[target_index].c_item.c
                synth_image = G_new.synthesis(projected_w_steps[-1].unsqueeze(0).to(device), c=cam_i, noise_mode='const')['image']
                synth_image = (synth_image + 1) * (255 / 2)
                synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
                views.append(np.concatenate([images[target_index].t_uint8, synth_image], axis=0))
            G_new.cpu()
            video.append_data(np.concatenate(views, axis=1))
        video.close()

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    run_projection()
