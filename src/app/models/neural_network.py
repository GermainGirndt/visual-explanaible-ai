from dotenv import load_dotenv
import os

import torch
from torchvision.models import EfficientNet_V2_S_Weights, efficientnet_v2_s, EfficientNet_V2_L_Weights, efficientnet_v2_l
from PIL import Image
from app.config import STATIC_DIR

class NeuralNetwork:
    img_tensor = []
    def __init__(self):
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
            self.weights = EfficientNet_V2_S_Weights.IMAGENET1K_V1
            self.model = efficientnet_v2_s(weights=self.weights)
        elif MODEL_SIZE == "large":
            self.weights = EfficientNet_V2_L_Weights.IMAGENET1K_V1
            self.model = efficientnet_v2_l(weights=self.weights)
        else:
            raise ValueError(f"MODEL_SIZE environment variable must be either 'small' or 'large'. Found: {MODEL_SIZE}")

    
    def classify(self, image_url:str):

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
        self.model = self.model.to(torch_device)
        self.model.eval()
        
        preprocess = self.weights.transforms()
        img = Image.open("src/app/views" + image_url).convert("RGB")
        # Unsqueeze to add a new single-item batch dimension
        # Before: [channels, height, width] = (3, H, W)
        # After: [batch_size, channels, height, width] = (1, 3, H, W)
        # In other words, it inserts a new dimension at index 0 to represent the batch size of 1
        # It's necessary because PyTorch models expect input tensors to have a batch dimension
        self.img_tensor = preprocess(img).unsqueeze(0).to(torch_device)
        self.img_tensor.requires_grad_()

        # -------------------------------------------------------------------
        # 5. Run inference
        # -------------------------------------------------------------------

        # Normally, PyTorch automatically tracks every operation on tensors so it can later compute gradients for training (via backpropagation).
        # That tracking uses extra memory and slows things down — but it’s only needed during training.
        with torch.no_grad():
            outputs = self.model(self.img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)


        # -------------------------------------------------------------------
        # 6. Get top-5 predictions
        # -------------------------------------------------------------------
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        categories = self.weights.meta["categories"]

        return  [ {"class_name": categories[top5_catid[0]], "confidence":  top5_prob[0].item(), "class_nr":top5_catid[0]},
                    {"class_name":categories[top5_catid[1]], "confidence": top5_prob[1].item(), "class_nr":top5_catid[1]},
                    {"class_name": categories[top5_catid[2]], "confidence": top5_prob[2].item(), "class_nr":top5_catid[2]},
                    {"class_name": categories[top5_catid[3]], "confidence": top5_prob[3].item(), "class_nr":top5_catid[3]},
                    {"class_name": categories[top5_catid[4]], "confidence": top5_prob[4].item(), "class_nr":top5_catid[4]},
                ]
