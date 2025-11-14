from fastapi import Request
from .base_view import BaseView

# ---------------------------------------------------------------------------
# explanation_view.py
# ---------------------------------------------------------------------------

class ExplanationView(BaseView):
    template_name = "explanation.html"

    def render_explanation(self, request: Request, image_url: str, heatmap_url: str, selected_class: str):
        return self.render(
            request,
            {
                "image_url": image_url,
                "heatmap_url": heatmap_url,
                "selected_class": selected_class,
            },
        )
