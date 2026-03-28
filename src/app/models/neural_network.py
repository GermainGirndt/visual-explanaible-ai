from dotenv import load_dotenv
import os

from pyparsing import ABC, abstractmethod
import torch
from torchvision.models import EfficientNet_V2_L_Weights, efficientnet_v2_l, resnet152, ResNet152_Weights
from PIL import Image as PIL_Image

from app.models.predictions import Predictions
from app.models.image import Image 

from app.config import STATIC_DIR

class NeuralNetwork(ABC):
    
    @abstractmethod
    def classify(self, image: Image) -> Predictions:
        pass

class EfficientNetv2(NeuralNetwork):
    img_tensor = []
    currentImage = []
    weights = []
    def __init__(self):        
        self.weights = EfficientNet_V2_L_Weights.IMAGENET1K_V1
        self.model = efficientnet_v2_l(weights=self.weights)
     
    
    def classify(self, image: Image) -> Predictions:
        
        if not image:
            raise ValueError("No image provided for classification.")
        
        if not image.image_url:
            raise ValueError("Image URL is empty.")
        
        self.currentImage = image
        load_dotenv()
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
        img = PIL_Image.open("src/app/views" + image.image_url).convert("RGB")
        
        # Unsqueeze to add a new single-item batch dimension
        # Before: [channels, height, width] = (3, H, W)
        # After: [batch_size, channels, height, width] = (1, 3, H, W)
        # In other words, it inserts a new dimension at index 0 to represent the batch size of 1
        # It's necessary because PyTorch models expect input tensors to have a batch dimension
        self.img_tensor = preprocess(img).unsqueeze(0).to(torch_device)
        self.img_tensor.requires_grad_()


        with torch.enable_grad():
            outputs = self.model(self.img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        probabilities_list = [prob.item() for prob in probabilities]
        class_names = self.weights.meta["categories"]
             
        predictions = Predictions(class_names=class_names, probabilities=probabilities_list)
        
        return predictions
    

class ResNet(NeuralNetwork):
    img_tensor = []
    currentImage = []
    weights = []
    def __init__(self):        
        self.weights = ResNet152_Weights.DEFAULT
        self.model = resnet152(weights=self.weights)
    
    def classify(self, image: Image) -> Predictions:
        
        if not image:
            raise ValueError("No image provided for classification.")
        
        if not image.image_url:
            raise ValueError("Image URL is empty.")
        
        self.currentImage = image
        load_dotenv()
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
        img = PIL_Image.open("src/app/views" + image.image_url).convert("RGB")
        
        # Unsqueeze to add a new single-item batch dimension
        # Before: [channels, height, width] = (3, H, W)
        # After: [batch_size, channels, height, width] = (1, 3, H, W)
        # In other words, it inserts a new dimension at index 0 to represent the batch size of 1
        # It's necessary because PyTorch models expect input tensors to have a batch dimension
        self.img_tensor = preprocess(img).unsqueeze(0).to(torch_device)
        self.img_tensor.requires_grad_()


        with torch.enable_grad():
            outputs = self.model(self.img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        probabilities_list = [prob.item() for prob in probabilities]
        class_names = self.weights.meta["categories"]
             
        predictions = Predictions(class_names=class_names, probabilities=probabilities_list)
        
        return predictions
    
