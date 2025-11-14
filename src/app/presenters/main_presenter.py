from app.views.image_view import ImageView
from app.views.prediction_view import PredictionView
from app.views.explanation_view import ExplanationView

from app.models.image import Image
from app.models.neural_network import NeuralNetwork
from app.models.prediction import Prediction
from app.models.explanation import Explanation
from app.models.explainable_ai_technique import ExplainableAITechnique

class MainPresenter:
     def __init__(self):
        self.image_view = ImageView()
        self.prediction_view = PredictionView()
        self.explanation_view = ExplanationView()

        self.model = NeuralNetwork()
        self.explainable_ai_technique = ExplainableAITechnique()
    
    # TODO: Add methods to coordinate between views and models