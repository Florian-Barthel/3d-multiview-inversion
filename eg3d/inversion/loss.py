import torch
import torch.nn.functional as F

from models.encoders.model_irse import Backbone


def mse(target_images: torch.tensor, synth_images: torch.tensor):
    return (target_images - synth_images).square().mean()


def perc(
        target_feature: torch.tensor,
        synth_images: torch.tensor,
        vgg: torch.nn.Module,
        downsampling: bool,
):
    # Downsample image to 256x256 if it's larger than that. VGG was built for 224x224 images.
    if synth_images.shape[2] > 256 and downsampling:
        synth_images = F.interpolate(synth_images, size=(256, 256), mode='area')

    # Features for synth images.
    synth_features = vgg(synth_images)  # , resize_images=False, return_lpips=True)
    return (target_feature.to("cuda") - synth_features).square().sum().mean()


def noise_reg(noise_bufs):
    reg_loss = 0
    for v in noise_bufs.values():
        noise = v[None, None, :, :]  # must be [1,1,H,W] for F.avg_pool2d()
        while True:
            reg_loss += (noise * torch.roll(noise, shifts=1, dims=3)).mean() ** 2
            reg_loss += (noise * torch.roll(noise, shifts=1, dims=2)).mean() ** 2
            if noise.shape[2] <= 8:
                break
            noise = F.avg_pool2d(noise, kernel_size=2)
    return reg_loss


class IDLoss(torch.nn.Module):
    def __init__(self):
        super(IDLoss, self).__init__()
        self.facenet = Backbone(input_size=112, num_layers=50, drop_ratio=0.6, mode="ir_se")
        self.facenet.load_state_dict(torch.load("pretrained_models/model_ir_se50.pth"))
        self.face_pool = torch.nn.AdaptiveAvgPool2d((112, 112))
        self.facenet.eval()
        self.facenet = self.facenet.to("cuda")

    def extract_feats(self, x):
        if x.shape[2] > 256:
            x = F.interpolate(x, size=(256, 256), mode='area')
        x = x[:, :, 35:223, 32:220]  # Crop interesting region
        x = self.face_pool(x)
        x_feats = self.facenet(x)
        return x_feats[0]

    def forward(self, synth_image, target_image):
        x_feats = self.extract_feats(synth_image)
        y_feats = self.extract_feats(target_image)
        y_feats = y_feats.detach()
        return 1 - y_feats.dot(x_feats)
