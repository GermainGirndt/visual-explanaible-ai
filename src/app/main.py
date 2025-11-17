from typing import Union

from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel

# Import views/presenters
from app.views.image_view import ImageView
from app.views.prediction_view import PredictionView
from app.views.explanation_view import ExplanationView

from app.presenters.main_presenter import MainPresenter


# ---------------------------------------------------
# Initialize FastAPI app
# ---------------------------------------------------

app = FastAPI()


# ---------------------------------------------------
# Mount STATIC FILES (CSS, JS, images, uploads, etc.)
# ---------------------------------------------------

STATIC_DIR = Path(__file__).parent / "views" / "static"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

# ---------------------------------------------------
# Initialize Main Presenter
# ---------------------------------------------------

main_presenter = MainPresenter(app=app)
