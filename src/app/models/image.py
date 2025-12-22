from app.config import STATIC_DIR
import uuid


class Image:
    image_url: str = ""
    def __init__(self, image_url: str):
        self.image_url=image_url
        
    @staticmethod
    async def load_from(file):

        """Handle image upload and render preview page."""

        UPLOAD_DIR = STATIC_DIR / "uploads"
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        if file is None:
            return image_view.render_image_page(request, image_url="")
        
        image_uuid = uuid.uuid4()   
        # Save file to disk
        file_location = f"{UPLOAD_DIR}/{image_uuid}{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        image = Image(f"/static/uploads/{image_uuid}{file.filename}")
        return image
       