# 🧠 Requirements Analysis — Explainable AI Teaching App

## 🎯 User Story

> **As a professor of Applied Artificial Intelligence**,  
> I want a **graphical user interface** that demonstrates **explainable AI (xAI)**,  
> so I can visually teach how AI models explain their decisions to my students.

> 💬 _Why?_ Interactive visualization helps students better understand how models make decisions, bridging theory and practice.

---

## ✅ Must-Have Features

### 1. Image Loading & Display

- The app must **load** and **display images**.
- **Acceptance Criteria:**
  1. The app can load image files stored locally on the computer.
  2. The app can display loaded images directly in the browser.

> 💬 _Why?_ Loading local images allows the professor to use classroom or student-provided examples easily without extra setup.

---

### 2. Image Classification

- The app must **classify an image** using a neural network model.
- **Acceptance Criteria:**
  1. The app uses an **EfficientNetV2** model for classification.
  2. The classification results are rendered to the frontend.

> 💬 _Why?_ EfficientNetV2 provides a strong balance between accuracy and performance. Since the EfficientNetV2 models are generally smaller (some dozents to a few hundreds MBs size), they are appropriate for real-time demos running locally during class.

---

### 3. Explainable AI (xAI) Heatmap

- The app must **generate an explanation heatmap** for classified images.
- **Acceptance Criteria:**
  - The app uses the **Grad-CAM** method for generating explanations.
  - The generated headmap is going to be visually rendered over the image layer with some opacity.

> 💬 _Why?_ Grad-CAM is widely recognized, visually intuitive, and easy to demonstrate during lectures. Also, there's a good amont of learning resources on Grad-CAM available (e.g. articles, Youtube videos, etc...), which makes it a good initial step for introducing explainability visually.

---

### 4. Maintainability

- The app should be **easy to maintain**.
- **Acceptance Criteria:**
  - Documentation lists:
    - Programming languages used and version
    - Dependency versions and configuration details

> 💬 _Why?_ Good documentation ensures future contributors or students can reproduce and extend the system without configuration issues.

---

## 💡 Should-Have Features

### Extensibility

- The app should be **easily extensible** to support different models and xAI methods.
- **Acceptance Criteria:**
  1. The user can select among multiple image classification models and explanation processes.
  2. Once a model is chosen, only compatible explanation methods are selectable.

> 💬 _Why?_ Extensibility supports future research or student projects by allowing new models or xAI methods to be plugged in easily.

---

## 💭 Could-Have Features

### Support for Other Explanation Types

- The app could support **additional explanation formats**.
- **Acceptance Criteria:**
  - The system supports:
    1. **Text-based** explanations
    2. **Graphical** explanations

> 💬 _Why?_ Providing textual or graphical outputs can improve understanding and accessibility for different learning styles.

---

## 🚫 Won’t-Have (for Initial Release)

1. **Streaming or Batch Processing**

   - No real-time or batch image folder processing.
     > 💬 _Why?_ Simplifies the architecture and focuses on single-image interactivity for teaching.

2. **Advanced Explanation Techniques**

   - No **LIME**, **SHAP**, or **Integrated Gradients**.
   - No 3D or temporal visualizations.
     > 💬 _Why?_ These techniques are more complex to implement and visualize; Grad-CAM is enough for initial educational purposes.

3. **Responsive Design**

   - No responsive web UI.
     > 💬 _Why?_ The tool is meant for classroom or desktop use, not for general public deployment.

4. **App Deployment**

   - No app deployment.
     > 💬 _Why?_ The deployment of a (desktop/mobile) app unnecessarily increases the complexity of the project, which should focus on AI explainability. Also, since the user is a technical person, he is capable of executing the start scripts.

5. **Multi-Language Interface**

   - The interface will be **English-only**.
     > 💬 _Why?_ English is the standard in most AI teaching materials, and translation isn’t essential for the initial release.

6. **Docker Container**
   - No Docker container
     > 💬 _Why?_ Although Docker improves reproducibility, it adds unnecessary complexity for a locally run educational app. Since the tool runs on a single machine and users can install dependencies directly, containerization offers little practical benefit at this stage.
