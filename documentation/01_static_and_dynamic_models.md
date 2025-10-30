# Static and Dynamic Models

## Architectural Decision: Model-View-Controller (MVC)

### Context

The Explainable AI (xAI) Teaching App must:

1. Load and visualize images.
2. Classify them using a neural network model.
3. Generate an explanation utilizing a xAI technique.
4. Be maintainable, extensible, and easy to demonstrate live in a classroom.

### Why MVC

The MVC Architecture fulfill these requirements by providing a clear separation between:

- AI + Computation logic (Model)
- Graphic Visualization/Presentation logic (View)
- User Interaction (Controller)

Here is important to highlight that MVC architecture was mainly chosen to fulfill the maintainability and extensibility criteria, while maintaining a flexible and lightweight architecture.

#### ✅ Advantages of MVC

- Separation of concerns: Isolates computation, logic, and UI for easier maintenance.
- Extensibility: New models or xAI methods can be added by extending the model layer.
- Testability: Model and controller can be unit-tested independently from the view.
- Pedagogical clarity: Mirrors conceptual separation between data, processing, and presentation, useful in an educational setting.

#### ⚠️ Disadvantages of MVC

- Slightly more boilerplate code (e.g., additional classes for presenters and controllers).
- Requires disciplined coordination between components to avoid “fat controllers.”

### Static Model

#### Class Diagram: Coordination through the Controller Class

```mermaid
classDiagram

%% --------------------
%% Model Layer
%% --------------------
class Image {
    + static load_from(string path): Image
}

class Prediction {
    + float confidence
    + int class_nr
    + string class_name
}

class NeuralNetwork {
    + classify(Image image): Prediction
}

class ExplainableAITechnique {
    + explain(Prediction prediction, NeuralNetwork for_model): Explanation
}

class Explanation {
    - ExplainableAITechnique from_technique
}

%% --------------------
%% View Layer
%% --------------------
class ImagePresenter {
    + render(Image image)
}

class PredictionPresenter {
    + render(Prediction prediction, Image image)
}

class ExplanationPresenter {
    + render(Explanation explanation, Prediction prediction, Image image)
}

%% --------------------
%% Controller Layer
%% --------------------
class MainController {
    + load_image(string path)
    + classify_image()
    + explain_classification()
    + select_model(NeuralNetwork model)
    + select_explainable_ai_technique(ExplainableAITechnique technique)
}

%% --------------------
%% Relationships
%% --------------------
MainController --> Image
MainController --> NeuralNetwork
MainController --> ExplainableAITechnique
MainController --> Prediction
MainController --> Explanation

MainController --> ImagePresenter
MainController --> PredictionPresenter
MainController --> ExplanationPresenter

```

#### Class Diagram: Relationship between Models and Views

```mermaid
classDiagram
%% --------------------
%% Model Layer
%% --------------------
class Image {
    + static load_from(string path): Image
}

class NeuralNetwork {
    + classify(Image image): Prediction
}

class Prediction {
    + float confidence
    + int class_nr
    + string class_name
}

class ExplainableAITechnique {
    + explain(Prediction prediction, NeuralNetwork model): Explanation
}

class Explanation {
    - ExplainableAITechnique from_technique
}

%% --------------------
%% View Layer (Separate Web Pages)
%% --------------------
class ImagePresenter {
    + render(Image image)
}

class PredictionPresenter {
    + render(Prediction prediction, Image? image)
}

class ExplanationPresenter {
    + render(Explanation explanation, Prediction prediction, Image image)
}

%% --------------------
%% Relationships (Models)
%% --------------------
NeuralNetwork --> Image : "classifies"
NeuralNetwork --> Prediction : "produces"

ExplainableAITechnique --> NeuralNetwork : "uses"
ExplainableAITechnique --> Prediction : "uses"
ExplainableAITechnique --> Explanation : "produces"

Explanation --> ExplainableAITechnique : "derived from"

%% --------------------
%% Relationships (Views)
%% --------------------
ImagePresenter --> Image : "renders"

PredictionPresenter --> Prediction : "renders"
PredictionPresenter --> Image : "renders"

ExplanationPresenter --> Explanation : "renders"
ExplanationPresenter --> Prediction : "renders"
ExplanationPresenter --> Image : "renders"

```

### Dynamic Model

#### Sequence Diagram: Default Use Case

```mermaid

sequenceDiagram
    participant User
    participant MainController
    participant Image
    participant NeuralNetwork
    participant ExplainableAITechnique
    participant ImagePresenter
    participant PredictionPresenter
    participant ExplanationPresenter

    User->>MainController: select_model(NeuralNetwork model)
    MainController->>MainController: store model as current_model

    User->>MainController: select_explainable_ai_technique(ExplainableAITechnique technique)
    MainController->>MainController: store technique as current_technique

    User->>MainController: load_image(path)
    MainController->>Image: load_from(path)
    Image-->>MainController: image instance
    MainController->>ImagePresenter: render(image)

    User->>MainController: classify_image()
    MainController->>NeuralNetwork: classify(current_image)
    NeuralNetwork-->>MainController: Prediction
    MainController->>PredictionPresenter: render(prediction, current_image)

    User->>MainController: explain_classification()
    MainController->>ExplainableAITechnique: explain(prediction, current_model)
    ExplainableAITechnique-->>MainController: Explanation
    MainController->>ExplanationPresenter: render(explanation, prediction, current_image)
```
