import torch
from torch import Tensor
from typing import Any

from app.models.prediction import Prediction

class Predictions:

    def __init__(self, class_names: list[str], probabilities: list[float]):
        self.predictions = []
        
        for index, probability in enumerate(probabilities):
            prediction = Prediction(
                confidence=probability,
                class_id=index,
                class_name=class_names[index]
            )
            self.predictions.append(prediction)
        
        self.sorted_predictions = sorted(self.predictions, key=lambda p: p.confidence, reverse=True)
        

    
    def top_k(self, k:int) -> list[Prediction]:
        print(self)
        return self.sorted_predictions[:k]
    
    def __repr__(self):
        return f"Predictions({self.sorted_predictions[:5]}...)"
        
        
        
    