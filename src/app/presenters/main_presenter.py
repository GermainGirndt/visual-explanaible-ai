from app.views import image_view
from app.views.image_view import ImageView
from app.views.prediction_view import PredictionView
from app.views.explanation_view import ExplanationView

from app.models.image import Image
from app.models.neural_network import NeuralNetwork, EfficientNet
from app.models.predictions import Prediction
from app.models.explanation import Explanation
from app.models.explainable_ai_technique import ExplainableAITechnique, GradCam
from fastapi import FastAPI, Request, UploadFile, Form

from app.config import STATIC_DIR


class MainPresenter:
     def __init__(self, app: FastAPI):
        image_view = ImageView()
        prediction_view = PredictionView()
        explanation_view = ExplanationView()

        model: NeuralNetwork = EfficientNet()
        explainable_ai_technique = ExplainableAITechnique()
    
        @app.get("/")
        def home(request: Request):
            """Render the upload page."""
            return image_view.render_image_page(request)

        @app.post("/upload")
        async def upload_image(request: Request, file: UploadFile):

            image = await Image.load_from(file)

            # Render image preview page again
            return image_view.render_image_page(request, image_url=image.image_url)


        @app.post("/classify")
        async def classify(request: Request, image_url: str = Form(...)):
            image = Image(image_url=image_url)
            predictions = model.classify(image)
            top_five_class_predictions = predictions.top_k(5)
            
            return prediction_view.render_predictions(
                request=request,
                image=image,
                class_predictions=top_five_class_predictions
            )



        @app.post("/explain")
        async def explain(request: Request, image_url: str = Form(...), class_name:str = Form(...)):
           gradcam = GradCam()
           heatmap_url = gradcam.explain(model, image_url, class_name)
           return explanation_view.render_explanation(request, image_url=image_url, heatmap_url=heatmap_url, selected_class=class_name)

