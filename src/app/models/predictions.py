import torch
from torch import Tensor
from typing import Any

from app.models.prediction import Prediction

class Predictions:

    def __init__(self, class_names: Any, probabilities: Tensor):
        self.class_names = class_names
        self.probabilities = probabilities
    
    def top_k(self, k:int) -> list[Prediction]:
        """Returns the top-k predictions as a list of tuples (class_name, probability)."""
        
        topk_prob, topk_catid = torch.topk(self.probabilities, k)
        
        top_k_predictions = []
        
        for top_class_index in range(k):
            
            prediction = Prediction(
                confidence=topk_prob[top_class_index].item(),
                class_id=int(topk_catid[top_class_index]),
                class_name=self.class_names[topk_catid[top_class_index]]
            )
            top_k_predictions.append(prediction)
            
        return top_k_predictions
        
        
    