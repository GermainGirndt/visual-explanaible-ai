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

app = FastAPI()

image_view = ImageView()
main_presenter = MainPresenter()

# ---------------------------------------------------
# Mount STATIC FILES (CSS, JS, images, uploads, etc.)
# ---------------------------------------------------

STATIC_DIR = Path(__file__).parent / "views" / "static"


app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)



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

prediction_view = PredictionView()

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

