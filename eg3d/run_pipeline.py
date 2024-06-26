import subprocess
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class MultiWHandler:
    def __init__(
            self,
            network="networks/var3-128.pkl",
            dataset="../dataset_preprocessing/ffhq/1",
            num_steps=500,
            num_steps_pti=500,
            out_dir="out",
            num_targets=5,
            downsampling=True,
            continue_w="out/20231018-1447_multiview_7/499_projected_w.npz",
            use_interpolation=False,
            depth_reg=False,
            w_norm_reg=True,
            save_video=False
    ):
        self.args = []
        self.args.append(f"--network={network}")
        self.args.append(f"--target={dataset}")
        self.args.append(f"--num-steps={num_steps}")
        self.args.append(f"--num-steps-pti={num_steps_pti}")
        self.args.append(f"--outdir={out_dir}")
        self.args.append(f"--num-targets={num_targets}")
        self.args.append(f"--downsampling={downsampling}")
        self.args.append(f"--continue-w={continue_w}")
        self.args.append(f"--use-interpolation={use_interpolation}")
        self.args.append(f"--depth-reg={depth_reg}")
        self.args.append(f"--w-norm-reg={w_norm_reg}")
        self.args.append(f"--save-video={save_video}")
        self.python = "python"
        self.path_to_program = "multi_inversion_multi_w.py"
        subprocess.run([self.python, self.path_to_program, *self.args], shell=False)


class SingleWHandler:
    def __init__(
            self,
            network="networks/var3-128.pkl",
            dataset="../dataset_preprocessing/ffhq/2",
            num_steps=500,
            num_steps_pti=500,
            out_dir="out",
            num_targets=7,
            downsampling=True,
            optimize_cam=False,
            save_video=False
    ):
        self.args = []
        self.args.append(f"--network={network}")
        self.args.append(f"--target={dataset}")
        self.args.append(f"--num-steps={num_steps}")
        self.args.append(f"--num-steps-pti={num_steps_pti}")
        self.args.append(f"--outdir={out_dir}")
        self.args.append(f"--num-targets={num_targets}")
        self.args.append(f"--downsampling={downsampling}")
        self.args.append(f"--optimize-cam={optimize_cam}")
        self.args.append(f"--save-video={save_video}")

        # self.python = "/home/barthel/miniconda3/envs/eg3d_3/bin/python"
        self.python = "python"

        self.path_to_program = "multi_inversion.py"
        subprocess.run([self.python, self.path_to_program, *self.args], shell=False)


if __name__ == "__main__":
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/2", continue_w="out/20231020-1943_multiview_7_iter_500_500_data_2/499_projected_w.npz", num_targets=9, w_norm_reg=False)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/3", continue_w="out/20231023-1007_multiview_7_iter_500_500_data_3/499_projected_w.npz", num_targets=9, w_norm_reg=False)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/4", continue_w="out/20231023-1040_multiview_7_iter_500_500_data_4/499_projected_w.npz", num_targets=9, w_norm_reg=False)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/5", continue_w="out/20231023-1115_multiview_7_iter_500_500_data_5/499_projected_w.npz", num_targets=9, w_norm_reg=False)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/6", continue_w="out/20231023-1147_multiview_7_iter_500_500_data_6/499_projected_w.npz", num_targets=9, w_norm_reg=False)
    #
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/2", continue_w="out/20231020-1943_multiview_7_iter_500_500_data_2/499_projected_w.npz", num_targets=9)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/3", continue_w="out/20231023-1007_multiview_7_iter_500_500_data_3/499_projected_w.npz", num_targets=9)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/4", continue_w="out/20231023-1040_multiview_7_iter_500_500_data_4/499_projected_w.npz", num_targets=9)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/5", continue_w="out/20231023-1115_multiview_7_iter_500_500_data_5/499_projected_w.npz", num_targets=9)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/6", continue_w="out/20231023-1147_multiview_7_iter_500_500_data_6/499_projected_w.npz", num_targets=9)
    #
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/2", continue_w="out/20231020-1943_multiview_7_iter_500_500_data_2/499_projected_w.npz", use_interpolation=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/3", continue_w="out/20231023-1007_multiview_7_iter_500_500_data_3/499_projected_w.npz", use_interpolation=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/4", continue_w="out/20231023-1040_multiview_7_iter_500_500_data_4/499_projected_w.npz", use_interpolation=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/5", continue_w="out/20231023-1115_multiview_7_iter_500_500_data_5/499_projected_w.npz", use_interpolation=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/6", continue_w="out/20231023-1147_multiview_7_iter_500_500_data_6/499_projected_w.npz", use_interpolation=True)

    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/2", continue_w="out/20231020-1943_multiview_7_iter_500_500_data_2/499_projected_w.npz", use_interpolation=True, depth_reg=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/3", continue_w="out/20231023-1007_multiview_7_iter_500_500_data_3/499_projected_w.npz", use_interpolation=True, depth_reg=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/4", continue_w="out/20231023-1040_multiview_7_iter_500_500_data_4/499_projected_w.npz", use_interpolation=True, depth_reg=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/5", continue_w="out/20231023-1115_multiview_7_iter_500_500_data_5/499_projected_w.npz", use_interpolation=True, depth_reg=True)
    # MultiWHandler(dataset="../dataset_preprocessing/ffhq/6", continue_w="out/20231023-1147_multiview_7_iter_500_500_data_6/499_projected_w.npz", use_interpolation=True, depth_reg=True)

    # SingleWHandler(dataset="../dataset_preprocessing/ffhq/2", num_targets=5)
    # SingleWHandler(dataset="../dataset_preprocessing/ffhq/3", num_targets=5)
    # SingleWHandler(dataset="../dataset_preprocessing/ffhq/4", num_targets=5)
    # SingleWHandler(dataset="../dataset_preprocessing/ffhq/5", num_targets=5)
    # SingleWHandler(dataset="../dataset_preprocessing/ffhq/1", num_targets=1, save_video=True)
    # SingleWHandler(dataset="../dataset_preprocessing/ffhq/1", num_targets=5, save_video=True)

    MultiWHandler(dataset="../dataset_preprocessing/ffhq/1", num_targets=5, continue_w="out_sync/20231018-1447_multiview_7/499_projected_w.npz", use_interpolation=True, depth_reg=True, save_video=True)
