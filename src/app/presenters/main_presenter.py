from app.views import image_view
from app.views.image_view import ImageView
from app.views.prediction_view import PredictionView
from app.views.explanation_view import ExplanationView
from starlette.responses import RedirectResponse
from app.models.image import Image
from app.models.neural_network import NeuralNetwork, EfficientNet
from app.models.predictions import Prediction
from app.models.explanation import Explanation
from app.models.explainable_ai_technique import ExplainableAITechnique, GradCam
from fastapi import FastAPI, Request, UploadFile, Form

from app.config import STATIC_DIR


class MainPresenter:
     size = "large"
     image = []
     model: NeuralNetwork = EfficientNet("large")
     def __init__(self, app: FastAPI):
        image_view = ImageView()
        prediction_view = PredictionView()
        explanation_view = ExplanationView()
   
        
        explainable_ai_technique = ExplainableAITechnique()
    
        @app.get("/")
        def home(request: Request):
            """Render the upload page."""
            return image_view.render_nav_page(request, model_size=self.size)
        
        @app.get("/resize")
        def resize(request:Request):
            if self.image != []:
                return image_view.render_image_page(request, self.image.image_url, self.size)
            else:
                return image_view.render_nav_page(request, model_size=self.size)
                
        
        @app.post("/")
        def changeModelsize(request: Request, model_size: str = Form(...)):
             self.model = EfficientNet(model_size)
             self.size = model_size
             return RedirectResponse("/resize", status_code=303)
            
        @app.post("/upload")
        async def upload_image(request: Request, file: UploadFile):

            self.image = await Image.load_from(file)

            # Render image preview page again
            return image_view.render_image_page(request, self.image.image_url, self.size)


        @app.post("/classify")
        async def classify(request: Request, image_url: str = Form(...)):
            image = Image(image_url=image_url)
            predictions = self.model.classify(image)
            top_five_class_predictions = predictions.top_k(5)
            
            return prediction_view.render_predictions(
                request=request,
                image=image,
                class_predictions=top_five_class_predictions
            )



        @app.post("/explain")
        async def explain(request: Request, confidence:float = Form(...), class_id:int = Form(...), class_name:str = Form(...) ):
           prediction = Prediction(confidence, class_id, class_name)
           gradcam = GradCam()
           explanation = gradcam.explain(prediction, self.model)
           return explanation_view.render_explanation(request, image_url= self.model.currentImage.image_url, heatmap_url=explanation.heatmap_url, selected_class=class_name)

