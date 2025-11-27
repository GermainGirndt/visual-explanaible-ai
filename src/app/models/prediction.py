
class Prediction:

    def __init__(self, confidence: float, class_id: int, class_name: str):
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        
    
    def __repr__(self):
        return f"Prediction(class_id={self.class_id}, class_name='{self.class_name}', confidence={self.confidence})"
        
    