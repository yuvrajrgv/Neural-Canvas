# Neural Canvas AI

Remix Reality. Neural Magic.

Neural Canvas AI is a full-stack AI image transformation project built around FastAPI, Streamlit, OpenCV, and PyTorch. It turns face photos into stylized artwork while also supporting cartoon generation, cartoon face classification, image history, and account-based access.

The project is meant to feel like a real creative app, not just a model demo. A user can upload an image, choose a visual style, generate a result, compare the output, download it, and revisit earlier transformations from their history.

## Overview

Neural Canvas is designed for portrait-based image transformation. It includes classic computer-vision effects such as sketch and watercolor styles, plus deep-learning features for cartoon generation and cartoon face classification.

The goal of the project is to combine a practical backend, a usable app interface, and AI-powered image processing into one clean product experience. It shows how machine learning can be wrapped inside a complete application flow instead of being limited to notebooks or isolated scripts.

The experience focuses on a simple creative flow:

1. Upload a face image.
2. Select an artistic style.
3. Generate the transformed result.
4. View, compare, download, or revisit previous transformations.

## Screenshots

Add project screenshots in `docs/screenshots/` and replace these placeholder files with your actual images.

| App Area | Preview |
|---|---|
| Upload and style selection | ![Upload and style selection](docs/screenshots/upload-and-style.png) |
| Transformation result | ![Transformation result](docs/screenshots/transformation-result.png) |
| Gallery and history | ![Gallery and history](docs/screenshots/gallery-history.png) |
| Cartoon tools | ![Cartoon tools](docs/screenshots/cartoon-tools.png) |

## Features

| Feature | Description |
|---|---|
| Artistic transformations | Converts uploaded face photos into styles such as cartoon, pencil sketch, color pencil, edge-preserved painting, and watercolor. |
| Cartoon generation | Uses a trained generator model to create cartoon-style output from real portrait images. |
| Cartoon face classification | Classifies cartoon images against a set of public figure identities. |
| User accounts | Gives users a personalized space for their image activity and transformation history. |
| Image job history | Stores previous transformations so users can return to earlier results. |
| Result comparison | Presents the original and transformed images together for easy visual comparison. |
| Download support | Lets users save generated artwork after processing is complete. |

## Architecture

Neural Canvas is split into a simple app layer, backend layer, AI processing layer, and storage layer. The app interface handles the user workflow, while the backend manages authentication, image jobs, and calls into the image processing and model components.

```text
User
  |
  v
Streamlit App Interface
  |
  v
FastAPI Backend
  |
  +-- Authentication and user data
  +-- Image upload and job management
  +-- OpenCV style transformations
  +-- PyTorch cartoon generator and classifier
  |
  v
Storage
  +-- Uploaded images
  +-- Processed results
  +-- Trained model weights
```

The backend contains the main application logic, routers, database models, schemas, services, image processing code, and ML model loaders. The frontend contains the Streamlit app experience. Storage is used for original uploads and generated outputs, while the model weights support the cartoon generator and classifier.

## Transformation Styles

| Style | Description |
|---|---|
| Cartoon | Bold, illustrated cartoon look. |
| Pencil sketch | Grayscale hand-drawn sketch effect. |
| Color pencil | Colored pencil-inspired portrait style. |
| Edge preserve | Smooth painterly output with preserved facial edges. |
| Watercolor | Soft watercolor-like artistic rendering. |

## AI Capabilities

Neural Canvas includes two deep-learning features alongside the image transformation pipeline:

- A cartoon generator for creating full cartoon renderings from real portraits.
- A cartoon classifier trained to recognize 100 public figure identities in cartoon form.

These model-backed tools extend the app beyond standard filters and make it a more complete AI portrait platform.

## Product Experience

The app supports authentication, image upload, style selection, transformation status, result preview, download, and gallery history. The intended experience is direct and visual: users bring an image, choose a style, and receive an AI-generated artistic version they can keep.

## Project Scope

Neural Canvas AI is a full-stack image transformation project with:

- A backend service for authentication, image jobs, and AI processing.
- An app interface for uploading, transforming, and managing images.
- Local storage for uploaded and processed files.
- Trained model assets for cartoon generation and classification.

## Author

Built by [yuvrajrgv](https://github.com/yuvrajrgv).
