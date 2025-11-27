from fastapi import Request
from .base_view import BaseView
from app.models.prediction import Prediction
from app.models.image import Image


# ---------------------------------------------------------------------------
# prediction_view.py
# ---------------------------------------------------------------------------

class PredictionView(BaseView):
    template_name = "prediction.html"

    def render_predictions(self, request: Request, image: Image, class_predictions: list[Prediction]):
        return self.render(
            request,
            {
                "image_url": image.image_url,
                "class_predictions": class_predictions,
            },
        )

