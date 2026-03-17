# Static and Dynamic Models

## Architectural Decision: Model-View-Presenter (MVP)

### Context

The Explainable AI (xAI) Teaching App must:

1. Load and visualize images.
2. Classify them using a neural network model.
3. Generate an explanation utilizing a xAI technique.
4. Be maintainable, extensible, and easy to demonstrate live in a classroom.

### Why MVP with Supervising Presenter/Controller

The MVP Architecture fulfill these requirements by providing a clear separation between:

- AI + Computation logic (Model)
- Graphic Visualization logic (View)
- User Interaction (Presenter)

Here is important to highlight that MVP architecture was mainly chosen to fulfill the maintainability and extensibility criteria, while maintaining a flexible and lightweight architecture.

#### ✅ Advantages of MVP

- Separation of concerns: Isolates computation, logic, and UI for easier maintenance.
- Extensibility: New models or xAI methods can be added by extending the model layer.
- Testability: Model and presenter can be unit-tested independently from the view.
- Pedagogical clarity: Mirrors conceptual separation between data, processing, and presentation, useful in an educational setting.

#### ⚠️ Disadvantages of MVP

- Slightly more boilerplate code (e.g., additional classes for views and presenters).
- Requires disciplined coordination between components to avoid “fat presenters.”

#### Why not Model-View-Controller (MVC)

MVC could be an easier and lightweight alternative to MVP with less code and less component layers to implement.

Still, the advantages of the MVP overweight the drawbacks, specially regarding the non-functional requirements of manutenability and specially extensibility:

- views renders component only and do not depends on the model (no data-binding/observers)
- presenter (which controls the data flow) does not depend directly on an implemention of a views and do not manipulate view directly (instead, they just depend on an abstraction for listening to user inputs and passing model information to them)
- models do not notifies views for changes

For this reason, new functionalities (for instance for new neural-network models or new explainability techniques) in MVP could be inserted by subclassing/inheriting the existing classes. The same wouldn't be so easy in MVC, since model, view and controllers are more coupled.

### Static Model

#### Class Diagram: Coordination through the Presenter Class

The user interacts with the Presenter, which coordinates the other system classes.

```mermaid
classDiagram

%% --------------------
%% Model Layer
%% --------------------
class Image {
    + static load_from(string file) Image
}

class Prediction {
    + float confidence
    + int class_nr
    + string class_name
}

class NeuralNetwork {
    + classify(Image image) Predictions
}

class ExplainableAITechnique {
    + explain(Prediction prediction, NeuralNetwork model) Explanation
}

class Explanation {
    - string heatmap_url
}

%% --------------------
%% View Layer
%% --------------------
class ImageView {
    + render_nav_page(string model_type)
    + render_image_page(string image_url, string model_type)
}

class PredictionView {
    + render_predictions(list[Prediction] class_predictions, Image image)
}

class ExplanationView {
    + render_explanation(string image_url, string heatmap_url, string selected_class)
}

%% --------------------
%% Presenter Layer
%% --------------------
class MainPresenter {
    + upload_image(UploadFile file)
    + classify(string image_url)
    + explain(float confidence, int class_id, string class_name)
    + change_model_size(string model_type)
    + home()
    + resize()
}

%% --------------------
%% Relationships
%% --------------------
MainPresenter --> Image : "loads"
MainPresenter --> NeuralNetwork : "calls for classification"
MainPresenter --> ExplainableAITechnique : "calls for explanation"
MainPresenter --> Prediction : "stores and manages"
MainPresenter --> Explanation : "stores and manages"

MainPresenter --> ImageView : "renders via"
MainPresenter --> PredictionView : "renders via"
MainPresenter --> ExplanationView : "renders via"

```

Notes:

- 1: The main presenter could be in the future broken down into smaller presents
- 2: Specific views like "buttons" are accessory and therefore not shown in the class diagram modelling.

#### Class Diagram: Relationship between Models and Views

##### Views:

1. **ImageView:** renders the image
2. **PredictionView:** renders the image and the prediction
3. **ExplanationView:** renders the image, the prediction and the explanation

##### Models:

1. **Image:** Represents the input image loaded from disk; provides static method `load_from(file)` to import it.
2. **NeuralNetwork:** Performs the classification of an `Image`, producing a `Prediction`.
3. **Prediction:** Holds the classification output (class name, class number, and confidence score).
4. **ExplainableAITechnique:** Uses a `NeuralNetwork` and its `Prediction` to generate an `Explanation` (e.g., via Grad-CAM).
5. **Explanation:** Represents the result of the xAI process, typically (but not only) a visual heatmap derived from the model and prediction.

```mermaid
classDiagram
%% --------------------
%% Model Layer
%% --------------------
class Image {
    + static load_from(string file) Image
}

class NeuralNetwork {
    + classify(Image image) Predictions
}

class Predictions {
    + list[Prediction] predictions
    + top_k(int k) list[Prediction]
}

class Prediction {
    + float confidence
    + int class_nr
    + string class_name
}

class ExplainableAITechnique {
    + explain(Prediction prediction, NeuralNetwork model) Explanation
}

class Explanation {
    - string heatmap_url
}

%% --------------------
%% View Layer (Separate Web Pages)
%% --------------------
class ImageView {
    + render_nav_page(string model_type)
    + render_image_page(string image_url, string model_type)
}

class PredictionView {
    + render_predictions(list[Prediction] class_predictions, Image image)
}

class ExplanationView {
    + render_explanation(string image_url, string heatmap_url, string selected_class)
}

%% --------------------
%% Relationships (Models)
%% --------------------
NeuralNetwork --> Image : "classifies"
NeuralNetwork --> Predictions : "produces"
Predictions --> Prediction : "has"

ExplainableAITechnique --> NeuralNetwork : "uses"
ExplainableAITechnique --> Predictions : "uses"
ExplainableAITechnique --> Explanation : "produces"

Explanation --> ExplainableAITechnique : "derived from"

%% --------------------
%% Relationships (Views)
%% --------------------
ImageView --> Image : "renders"

PredictionView --> Predictions : "renders"
PredictionView --> Image : "renders"

ExplanationView --> Explanation : "renders"
ExplanationView --> Predictions : "renders"
ExplanationView --> Image : "renders"

```

### Dynamic Model

#### Sequence Diagram: Default Use Case

```mermaid

sequenceDiagram
    participant User
    participant MainPresenter
    participant Image
    participant NeuralNetwork
    participant ExplainableAITechnique
    participant ImageView
    participant PredictionView
    participant ExplanationView

    User->>MainPresenter: change_model_size(string model_type)
    MainPresenter->>MainPresenter: store model as current_model

    #User->>MainPresenter: select_explainable_ai_technique(ExplainableAITechnique technique)
    #MainPresenter->>MainPresenter: store technique as current_technique

    User->>MainPresenter: upload_image(file)
    MainPresenter->>Image: load_from(file)
    Image-->>MainPresenter: image instance
    MainPresenter->>ImageView: render_image_page(image_url, model_type)

    User->>MainPresenter: classify(image_url)
    MainPresenter->>NeuralNetwork: classify(image)
    NeuralNetwork-->>MainPresenter: Prediction
    MainPresenter->>PredictionView: render(class_predictions, image)

    User->>MainPresenter: explain(confidence, class_id, class_name)
    MainPresenter->>ExplainableAITechnique: explain(prediction, model)
    ExplainableAITechnique-->>MainPresenter: Explanation
    MainPresenter->>ExplanationView: render(image_url, heatmap_url, selected_class)
```
