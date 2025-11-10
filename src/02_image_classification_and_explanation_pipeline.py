
# TODO: Write an pipeline with image classification and explanation using GradCAM

from dotenv import load_dotenv
import os

import torch
from torchvision.models import EfficientNet_V2_S_Weights, efficientnet_v2_s, EfficientNet_V2_L_Weights, efficientnet_v2_l
from PIL import Image
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.cm as cm
# -------------------------------------------------------------------
# 1. Load environment variables
# -------------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------------
# 2. Load pre-trained weights and initialize the model
# -------------------------------------------------------------------

# ImageNet1K V1 is the data set used for training the model and producing the weights
# It contains 1k classes, 50k validation images and about 1.2 million training images
# The ImageNet-1K dataset is also known as ILSVRC-2012 is maintained by the ImageNet project, of the Stanford Vision and Princeton University (https://www.image-net.org)
# It's also available on Kaggle (https://www.kaggle.com/c/imagenet-object-localization-challenge/overview/description)
MODEL_SIZE = os.getenv("MODEL_SIZE")
print(f"Using model size: {MODEL_SIZE}")

if MODEL_SIZE is None:
    raise ValueError("MODEL_SIZE environment variable is not set.")
if MODEL_SIZE == "small":
    weights = EfficientNet_V2_S_Weights.IMAGENET1K_V1
    model = efficientnet_v2_s(weights=weights)
elif MODEL_SIZE == "large":
    weights = EfficientNet_V2_L_Weights.IMAGENET1K_V1
    model = efficientnet_v2_l(weights=weights)
else:
    raise ValueError(f"MODEL_SIZE environment variable must be either 'small' or 'large'. Found: {MODEL_SIZE}")

# -------------------------------------------------------------------
# 3. Set the model to evaluation mode and move to device
# -------------------------------------------------------------------
# TODO: TEST for CUDA if available

DEVICE = os.getenv("DEVICE")
print(f"Using device: {DEVICE}")

if DEVICE is None:
    raise ValueError("DEVICE environment variable is not set.")
elif DEVICE == "mps":
    if not torch.backends.mps.is_available():
        raise ValueError("MPS device is not available.")
elif DEVICE == "cuda":
    if not torch.cuda.is_available():
        raise ValueError("CUDA device is not available.")
elif DEVICE != "cpu":
    raise ValueError("DEVICE environment variable must be either 'cpu', 'cuda', or 'mps'.")

torch_device = torch.device(device=DEVICE)
model = model.to(torch_device)
model.eval()


# -------------------------------------------------------------------
# 4. Preprocess the image
# -------------------------------------------------------------------

IMAGE_PATH = os.getenv("IMAGE_PATH")
print(f"Using image path: {IMAGE_PATH}")
if IMAGE_PATH is None:
    raise ValueError("IMAGE_PATH environment variable is not set.")
elif IMAGE_PATH.strip() == "":
    raise ValueError("IMAGE_PATH environment variable is empty.")

# Initialize the Weight Transforms and apply them to the input image
# It includes the pre-processing steps that were applied to the images during training
# This ensures that the input images are in the same format as those used during training
# For instance, resizing, normalization, etc...
preprocess = weights.transforms()
img = Image.open(IMAGE_PATH).convert("RGB")

# Unsqueeze to add a new single-item batch dimension
# Before: [channels, height, width] = (3, H, W)
# After: [batch_size, channels, height, width] = (1, 3, H, W)
# In other words, it inserts a new dimension at index 0 to represent the batch size of 1
# It's necessary because PyTorch models expect input tensors to have a batch dimension
img_tensor = preprocess(img).unsqueeze(0).to(torch_device)

# Enable gradient tracking on the input tensor
# This consumes additional memory and computation, but it's necessary for GradCAM, since it requires gradients with respect to the input
img_tensor.requires_grad_()


# -------------------------------------------------------------------
# 5. Get top-5 predictions
# -------------------------------------------------------------------
outputs = model(img_tensor)
probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
top5_prob, top5_catid = torch.topk(probabilities, 5)
categories = weights.meta["categories"]

print("\nTop-5 Predictions:")
for i in range(top5_prob.size(0)):
    print(f"{categories[top5_catid[i]]:>25s}: {top5_prob[i].item():.4f}")


# ------------------------
# Utility: overlay heatmap
# ------------------------
def overlay_heatmap_on_pil(img_pil: Image.Image, heatmap: np.ndarray, alpha: float = 0.5):
    """
    img_pil: original PIL RGB image
    heatmap: 2D numpy array with values in [0,1], shape (H, W) matching img_pil.size when resized
    returns: PIL Image blended overlay
    """
    # convert heatmap to RGBA using matplotlib's colormap
    cmap = cm.get_cmap("jet")
    heatmap_colored = cmap(heatmap)[:, :, :3]  # (H, W, 3) RGB floats 0..1
    heatmap_img = Image.fromarray((heatmap_colored * 255).astype("uint8")).convert("RGB")
    heatmap_img = heatmap_img.resize(img_pil.size, resample=Image.BILINEAR)
    return Image.blend(img_pil.convert("RGB"), heatmap_img, alpha=alpha)


# ----------------------------------------------
#  Grad-CAM (convolutional activations)
# ----------------------------------------------
def find_last_conv_module(model):
    last = None
    for name, module in model.named_modules():
        # import inside to avoid top-level name collision
        if isinstance(module, torch.nn.Conv2d):
            last = module
    if last is None:
        raise RuntimeError("No Conv2d layer found in the model.")
    return last

def compute_gradcam(model, input_tensor, target_class=None):
    """
    Generic Grad-CAM that finds the last Conv2d layer automatically.
    Returns a normalized 2D numpy heatmap (H, W) in [0,1] in the preprocessed image spatial size.
    """
    model.eval()
    device = input_tensor.device

    activations = []
    gradients = []

    def forward_hook(module, inp, out):
        activations.append(out.detach())

    # use full backward hook for recent PyTorch
    def backward_hook(module, grad_in, grad_out):
        # grad_out is a tuple; grad_out[0] is the gradient w.r.t. the module output
        gradients.append(grad_out[0].detach())

    last_conv = find_last_conv_module(model)
    fh = last_conv.register_forward_hook(forward_hook)
    bh = last_conv.register_full_backward_hook(backward_hook)

    # forward and backward
    model.zero_grad()
    if input_tensor.grad is not None:
        input_tensor.grad.zero_()

    outputs = model(input_tensor)
    if target_class is None:
        target_class = outputs.argmax(dim=1).item()
    score = outputs[0, target_class]
    score.backward(retain_graph=False)

    # remove hooks
    fh.remove(); bh.remove()

    if not activations or not gradients:
        raise RuntimeError("Failed to capture activations/gradients for Grad-CAM.")

    act = activations[0].cpu()  # shape (1, C, Hf, Wf)
    grad = gradients[0].cpu()   # shape (1, C, Hf, Wf)

    act = act[0]  # (C, Hf, Wf)
    grad = grad[0]  # (C, Hf, Wf)

    # global-average-pool gradients over spatial dims -> channel weights
    weights = grad.mean(dim=(1, 2))          # (C,)

    # weighted sum of feature maps
    cam = torch.sum(weights[:, None, None] * act, dim=0)  # (Hf, Wf)
    cam = F.relu(cam)

    cam = cam - cam.min()
    cam = cam / (cam.max() + 1e-8)
    cam_np = cam.numpy()

    return cam_np


# ------------------------------
#  usage and saving file
# ------------------------------

#  Grad-CAM

for rank, class_idx in enumerate(top5_catid):
    class_idx = class_idx.item()
    class_name = categories[class_idx]
    print(f"\nGenerating Grad-CAM for: {class_name}")

    gradcam_map = compute_gradcam(model, img_tensor, target_class=class_idx)

    # Resize and overlay
    gradcam_resized = Image.fromarray((gradcam_map * 255).astype("uint8")).resize(img.size, resample=Image.BILINEAR)
    gradcam_np = np.array(gradcam_resized) / 255.0

    overlay = overlay_heatmap_on_pil(img, gradcam_np, alpha=0.5)
    filename = f"src/output/gradcam_top{rank+1}_{class_name.replace(' ', '_')}.png"
    overlay.save(filename)
    print(f" Saved: {filename}")