from app.views import image_view
from app.views.image_view import ImageView
from app.views.prediction_view import PredictionView
from app.views.explanation_view import ExplanationView

from app.models.image import Image
from app.models.neural_network import NeuralNetwork
from app.models.prediction import Prediction
from app.models.explanation import Explanation
from app.models.explainable_ai_technique import ExplainableAITechnique
from fastapi import FastAPI, Request, UploadFile, Form

class MainPresenter:
     def __init__(self, app: FastAPI):
        image_view = ImageView()
        prediction_view = PredictionView()
        explanation_view = ExplanationView()

        model = NeuralNetwork()
        explainable_ai_technique = ExplainableAITechnique()
    
        @app.get("/")
        def home(request: Request):
            """Render the upload page."""
            return image_view.render_image_page(request)

        @app.post("/upload")
        async def upload_image(request: Request, file: UploadFile):

            """Handle image upload and render preview page."""
            pass

            """ 
            UPLOAD_DIR = STATIC_DIR / "uploads"
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

            if file is None:
                return image_view.render_image_page(request, image_url=None)
            
            # Save file to disk
            file_location = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_location, "wb") as f:
                f.write(await file.read())

            image_url = f"/static/uploads/{file.filename}"

            # Render image preview page again
            return image_view.render_image_page(request, image_url=image_url)
            """

        @app.post("/classify")
        async def classify(request: Request, image_url: str = Form(...)):
            # fake model here for demo
            def mock_top5():
                return [
                    {"class_name": "Golden Retriever", "confidence": 0.82, "class_nr": 207},
                    {"class_name": "Labrador", "confidence": 0.10, "class_nr": 208},
                    {"class_name": "Beagle", "confidence": 0.03, "class_nr": 209},
                    {"class_name": "Bulldog", "confidence": 0.025, "class_nr": 210},
                    {"class_name": "Poodle", "confidence": 0.015, "class_nr": 211},
                ]
                
            predictions = mock_top5()  # replace with your real model
            return prediction_view.render_predictions(
                request=request,
                image_url=image_url,
                predictions=predictions
            )

