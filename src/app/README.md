### Implementation of MVP with FastAPI

#### Main Components

- Model (AI + Computation logic) -> PyTorch (EfficientNetV2 + Grad-CAM)
- View (Graphic Visualization) -> Jinja2
- Presenter (User Interaction) -> FastAPI

#### Folder structure

```
/app
 ├── main.py               <- FastAPI app & routing (presenter)
 ├── models/               <- EfficientNetV2, Grad-CAM classes (model)
 ├── presenters/           <- Presenter classes orchestrating logic
 ├── templates/            <- HTML/Jinja2 frontend (view)
 ├── static/               <- CSS / JS / Heatmap overlay images
 └── views/                <- Optional view abstraction if desired
```
