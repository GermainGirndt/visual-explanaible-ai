
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
from app.config import STATIC_DIR

class ExplainableAITechnique:
    
    def explain(self, model, image_url, class_name):
        pass
    

class GradCam(ExplainableAITechnique):
     def explain(self, model, image_url, class_name):

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
        img = Image.open("src/app/views" + image_url).convert("RGB")
        categories = model.weights.meta["categories"]
        #  Grad-CAM
        # Create reverse lookup: classname → index
        classname_to_idx = {name: i for i, name in enumerate(categories)}

        # Grad-CAM
        class_idx = classname_to_idx[class_name]  

        gradcam_map = compute_gradcam(model.model, model.img_tensor, target_class=class_idx)

        # Resize and overlay
        gradcam_resized = Image.fromarray((gradcam_map * 255).astype("uint8")).resize(img.size, resample=Image.BILINEAR)
        gradcam_np = np.array(gradcam_resized) / 255.0

        overlay = overlay_heatmap_on_pil(img, gradcam_np, alpha=0.5)
        filename = f"src/app/views/static/gradcam_{class_name.replace(' ', '_')}.png"
        overlay.save(filename)
        name = f"static/gradcam_{class_name.replace(' ', '_')}.png"
        return name