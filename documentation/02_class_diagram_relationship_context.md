### Relationship Context

```mermaid
classDiagram
%% --------------------
%% Model Layer
%% --------------------
class Image {
    + static load_from(string path): Image
}

class NeuralNetwork {
    + classify(Image image): PredictionResult
}

class PredictionResult {
    + float confidence
    + int class_nr
    + string class_name
}

class ExplainableAITechnique {
    + explain(PredictionResult result, NeuralNetwork model): Explanation
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

class PredictionResultPresenter {
    + render(PredictionResult result, Image? image)
}

class ExplanationPresenter {
    + render(Explanation explanation, PredictionResult result, Image image)
}

%% --------------------
%% Relationships (Models)
%% --------------------
NeuralNetwork --> Image : "classifies"
NeuralNetwork --> PredictionResult : "produces"

ExplainableAITechnique --> NeuralNetwork : "uses"
ExplainableAITechnique --> PredictionResult : "uses"
ExplainableAITechnique --> Explanation : "produces"

Explanation --> ExplainableAITechnique : "derived from"

%% --------------------
%% Relationships (Views)
%% --------------------
ImagePresenter --> Image : "renders"

PredictionResultPresenter --> PredictionResult : "renders"
PredictionResultPresenter --> Image : "optional thumbnail"

ExplanationPresenter --> Explanation : "renders overlay"
ExplanationPresenter --> PredictionResult : "uses metadata"
ExplanationPresenter --> Image : "renders base image"

```
