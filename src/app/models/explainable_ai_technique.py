
from dotenv import load_dotenv
import os
import uuid
import torch
from torchvision.models import EfficientNet_V2_S_Weights, efficientnet_v2_s, EfficientNet_V2_L_Weights, efficientnet_v2_l
from PIL import Image
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.cm as cm
from app.models.prediction import Prediction
from app.models.neural_network import NeuralNetwork
from app.models.explanation import Explanation
from app.config import STATIC_DIR
from lime import lime_image
from skimage.segmentation import mark_boundaries, slic


class ExplainableAITechnique:
    
    #def explain(self, model, image_url, class_name):
    def explain(self, prediction:Prediction, model:NeuralNetwork):
        pass
    

class GradCam(ExplainableAITechnique):
     def explain(self, prediction:Prediction, model:NeuralNetwork):

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
        img = Image.open("src/app/views" + model.currentImage.image_url).convert("RGB")
      
        # Grad-CAM
        class_idx = prediction.class_id

        gradcam_map = compute_gradcam(model.model, model.img_tensor, target_class=class_idx)

        # Resize and overlay
        gradcam_resized = Image.fromarray((gradcam_map * 255).astype("uint8")).resize(img.size, resample=Image.BILINEAR)
        gradcam_np = np.array(gradcam_resized) / 255.0
        
        image_uuid = uuid.uuid4()  
        overlay = overlay_heatmap_on_pil(img, gradcam_np, alpha=0.5)
        filename = f"src/app/views/static/gradcam_{image_uuid}_{prediction.class_name.replace(' ', '_')}.png"
        overlay.save(filename)
        explanation = Explanation(f"static/gradcam_{image_uuid}_{prediction.class_name.replace(' ', '_')}.png")
        return explanation
    
    
    

class LIME(ExplainableAITechnique):
    
    
    def explain(self, prediction:Prediction, model:NeuralNetwork):
        def lime_predict(images: np.ndarray):

            model.model.eval()
            batch = []
            DEVICE = os.getenv("DEVICE")
            
            for img_np in images:
                img_pil = Image.fromarray(img_np.astype("uint8"), mode="RGB")
                preprocess = model.weights.transforms() 
                tensor = preprocess(img_pil).unsqueeze(0)
                batch.append(tensor)
                
            torch_device = torch.device(device=DEVICE)
            
            batch = torch.cat(batch, dim=0).to(torch_device)

            with torch.no_grad():
                outputs = model.model(batch)
                probs = F.softmax(outputs, dim=1)

            return probs.cpu().numpy()
        
        def color_lime_regions(img_np, mask, color=(255, 0, 0), alpha=0.6):

            overlay = img_np.copy()
            color_layer = np.zeros_like(img_np)
            color_layer[:] = color

            overlay[mask == 1] = (
                (1 - alpha) * overlay[mask == 1] +
                alpha * color_layer[mask == 1]
            )

            return Image.fromarray(overlay.astype("uint8"))

    
        img = Image.open("src/app/views" + model.currentImage.image_url).convert("RGB")
        img_np = np.array(img)
        class_idx = prediction.class_id

        explainer = lime_image.LimeImageExplainer()




        explanation = explainer.explain_instance(
            img_np,
            lime_predict,
            labels=[class_idx],     
            hide_color=0,
            num_samples=100 ,       # increase for better quality
            segmentation_fn=lambda img: slic(
             img,
             n_segments=30,
             compactness=10,
             start_label=0
            )
            )
        
        
       
        # Resize and overlay
        lime_img, lime_mask = explanation.get_image_and_mask(
            label=class_idx,
             positive_only=True,
             num_features=3,
             hide_rest=True
            )

        lime_overlay = Image.fromarray(
            (mark_boundaries(lime_img / 255.0, lime_mask) * 255).astype("uint8")
            )
        colored = color_lime_regions(
        img_np=lime_img,
        mask=lime_mask,
        color=(255, 0, 0), #red
        alpha=0.7
        )
        image_uuid = uuid.uuid4()
        filename = f"src/app/views/static/lime_{image_uuid}_{prediction.class_name.replace(' ', '_')}.png"
        colored.save(filename)
        explanation = Explanation(f"static/lime_{image_uuid}_{prediction.class_name.replace(' ', '_')}.png")
        return explanation