from fastapi import Request
from .base_view import BaseView

# ---------------------------------------------------------------------------
# image_view.py
# ---------------------------------------------------------------------------

class ImageView(BaseView):
    template_name = "index.html"

    def render_image_page(self, request: Request, image_url: str | None = None):
        print(f"Template: {self.template_name}")
        print(f"Request received: {request}")
        print(f"Rendering image page with image_url: {image_url}")
        return self.render(request, {"image_url": image_url})

