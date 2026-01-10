from fastapi import Request
from .base_view import BaseView

# ---------------------------------------------------------------------------
# image_view.py
# ---------------------------------------------------------------------------

class ImageView(BaseView):
    template_name = "index.html"

    def render_nav_page(self, request: Request, model_type:str| None = None):
        return self.render(request, { "model_type": model_type})
    
    def render_image_page(self, request: Request, image_url: str, model_type:str| None = None):
        return self.render(request, {"image_url": image_url, "model_type": model_type})

