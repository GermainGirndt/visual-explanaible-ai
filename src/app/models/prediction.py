
class Prediction:

    def __init__(self, confidence: float, class_id: int, class_name: str):
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        
    