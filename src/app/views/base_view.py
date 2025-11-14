# base_view.py
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path

# Configure templates directory (relative to views folder)
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class BaseView:
    template_name: str = 'Base View Template'

    def render(self, request: Request, context: dict):
        if not self.template_name:
            raise ValueError("template_name must be set in subclasses")

        # all templates receive the Request
        context = {"request": request, **context}
        return templates.TemplateResponse(self.template_name, context)
