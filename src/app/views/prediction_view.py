from fastapi import Request
from .base_view import BaseView


# ---------------------------------------------------------------------------
# prediction_view.py
# ---------------------------------------------------------------------------

class PredictionView(BaseView):
    template_name = "prediction.html"

    def render_predictions(self, request: Request, image_url: str, predictions: list):
        return self.render(
            request,
            {
                "image_url": image_url,
                "predictions": predictions,
            },
        )

