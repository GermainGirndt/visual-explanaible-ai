# visual-explanaible-ai

### Project Setup

For setting up the project on your machine, execute the following steps:

```
# Ensure Python version is 3.10.14
python --version

# Create a Virtual Environment
python -m venv venv

# Execute the Virtual Environment
source venv/bin/activate # Example for MacOS/Linux

# Install the required libraries
python install -r requirements.txt

# Create a new .env file according to the template
cp .env.example .env
```

### Project Executing

After configuring your `.env` file according to your system specs, run:

```
python src/01_image_classification_pipeline.py
```

### Project

### Notes

#### Pytorch

- The install command for Pytorch may be different depending on the user machine. If there's any incompatibility, check the following website:
  https://pytorch.org/get-started/locally/

### VSCODE Setup for Documentation

If you're using VSCode, it is recommend to use following Markdown plugins:

```
# Markdown Syntax Highlightning
bpruitt-goddard.mermaid-markdown-syntax-highlighting

# Markdown Previewer 1
hd101wyy.markdown-preview-enhanced

# Markdown Previewer 2 (Alternative)
yzhang.markdown-all-in-one

# Mermaid for Markdown (for generating the Mermaid Diagrams)
bierner.markdown-mermaid
```
