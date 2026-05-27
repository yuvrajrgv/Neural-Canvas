[README.md](https://github.com/user-attachments/files/28308588/README.md)
<div align="center">

# 🎨 Toonify AI

### *Remix Reality. Neural Magic.*

**Transform your face into a cartoon, pencil sketch, watercolor painting, and more — powered by deep learning.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)

</div>

---

## 📸 UI Screenshots

> **To add your screenshots:** Create a `docs/screenshots/` folder in your repo, drop your images there, and replace the placeholder paths below.

### Landing Page
![Landing Page](docs/screenshots/landing.png)
*The Toonify landing page — tagline "Remix Reality. Neural Magic." with feature highlights.*

### Authentication Screen
![Auth Screen](docs/screenshots/auth.png)
*Clean Sign In / Create Account tabs with a feature summary panel on the left.*

### Dashboard — Upload & Transform
![Dashboard Upload](docs/screenshots/dashboard-upload.png)
*Drag-and-drop upload panel with style selector. Choose your art style before hitting Transform.*

### Transformation Result
![Transform Result](docs/screenshots/dashboard-result.png)
*Side-by-side original vs. transformed image with download button and job metadata.*

### Gallery / History
![Gallery](docs/screenshots/gallery.png)
*All previous transformation jobs — filterable by style and status, with quick delete.*

### Cartoon Classifier
![Classifier](docs/screenshots/classifier.png)
*Upload a cartoon image to identify which of the 100 recognized public figures it resembles.*

### Cartoon Generator
![Generator](docs/screenshots/generator.png)
*GAN-based generator — upload a real photo and produce a full cartoon rendering.*

---

## 📖 What is Toonify?

Toonify is a full-stack AI-powered image transformation platform. Upload any photo of a face and apply one of **5 artistic styles** using computer vision and deep learning models. It also ships with:

- A **GAN-based cartoon generator** (trained from scratch — see `Cartoon_Generator_Training.ipynb`)
- A **cartoon face classifier** that recognizes 100 public figures in cartoon form
- A full **user authentication** system with JWT tokens
- A **job queue** for async image processing with real-time status polling
- A **Streamlit frontend** and a **raw HTML/CSS/JS** frontend (both connect to the same backend)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 **5 Art Styles** | Cartoon, Pencil Sketch, Color Pencil, Edge Preserve, Watercolor |
| 🎭 **Face Classifier** | Recognizes 100 celebrities from cartoon images |
| 🤖 **GAN Generator** | Deep learning–based cartoon generation from real photos |
| 🔐 **JWT Auth** | Secure sign-up/sign-in with access + refresh token rotation |
| 🗂️ **Job History** | Full transformation history per user with download support |
| 📊 **Live Status** | Real-time job polling — `pending → processing → completed` |
| 📁 **File Management** | Upload, process, download, and delete jobs |
| ⚡ **Fast API** | FastAPI backend with async processing and rate limiting |

---

## 🏗️ Architecture

```
Toonify/
├── backend/                   # FastAPI server
│   ├── app/
│   │   ├── main.py            # App entry point, CORS, router mounts
│   │   ├── database.py        # SQLAlchemy DB setup
│   │   ├── core/              # Config, security, dependencies
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── routers/           # Route handlers (auth, images, cartoon)
│   │   ├── services/          # Business logic layer
│   │   ├── image_processing/  # OpenCV transformation pipeline
│   │   ├── ml/                # ML model loaders & inference
│   │   └── utils/             # Helpers, file utils
│   ├── ml_weights/            # Trained model weight files (*.pth)
│   ├── notebooks/
│   │   ├── Cartoon_Generator_Training.ipynb   # GAN training notebook
│   │   ├── cartoon_model_gen.ipynb            # Generator inference
│   │   └── cartoon_model_classify.ipynb       # Classifier training & eval
│   └── requirements.txt
│
├── frontend/                  # Two frontend options
│   ├── index.html             # Landing page (pure HTML/CSS/JS)
│   ├── dashboard.html         # App dashboard (HTML/CSS/JS)
│   ├── css/                   # Stylesheets
│   ├── js/                    # auth.js, api.js, main.js
│   ├── app.py                 # Streamlit entry point
│   ├── views.py               # All Streamlit page/component views
│   ├── utils.py               # API call helpers for Streamlit
│   └── styles.py              # Streamlit custom CSS & components
│
└── storage/
    ├── uploads/               # Original uploaded images
    └── processed/             # Transformed output images
```

---

## 🎨 Transformation Styles

| Style | Description | Tech |
|---|---|---|
| `cartoon` | Classic bold-outline cartoon effect | OpenCV bilateral filter + edge mask |
| `pencil_sketch` | Grayscale pencil drawing | OpenCV pencil sketch |
| `color_pencil` | Artistic colored pencil | OpenCV color pencil |
| `edge_preserve` | Smooth, edge-preserving painterly look | OpenCV edge-preserving filter |
| `watercolor` | Soft watercolor painting | OpenCV stylization |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Node.js (optional, for serving the HTML frontend locally)

---

### 1. Clone the Repository

```bash
git clone https://github.com/yuvrajrgv/Toonify.git
cd Toonify
```

---

### 2. Set Up the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
DEBUG=True

# PostgreSQL connection string
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/toonify

# JWT settings
SECRET_KEY=your-very-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File storage paths (relative to project root)
UPLOAD_DIR=storage/uploads
PROCESSED_DIR=storage/processed
MAX_FILE_SIZE=10485760    # 10 MB

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

#### Create the Database

```bash
# In PostgreSQL
createdb toonify

# Run migrations with Alembic
alembic upgrade head
```

#### Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be live at **`http://localhost:8000`**.  
Interactive API docs: **`http://localhost:8000/docs`**

---

### 3a. Run the Streamlit Frontend

```bash
cd frontend

# Install frontend dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run app.py
```

Opens at **`http://localhost:8501`**

---

### 3b. Run the HTML Frontend

```bash
cd frontend

# Serve with Python's built-in server
python -m http.server 8080
```

Opens at **`http://localhost:8080`**

> **Note:** The HTML frontend expects the backend running at `http://localhost:8000`. No build step needed.

---

## 🔌 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login/form` | Sign in (OAuth2 form) → returns JWT tokens |

### Image Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/images/upload` | Upload image with a style parameter |
| `POST` | `/images/{job_id}/process` | Trigger processing for an uploaded job |
| `GET` | `/images/{job_id}` | Get job status and metadata |
| `GET` | `/images/` | List all jobs for the current user |
| `DELETE` | `/images/{job_id}` | Delete a job and its files |
| `GET` | `/images/download/{job_id}` | Download the processed image |

### Image File Serving

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/images/file/{job_id}/original` | Serve original uploaded image |
| `GET` | `/images/file/{job_id}/processed` | Serve processed/transformed image |
| `GET` | `/images/file/{job_id}/comparison` | Serve side-by-side comparison image |

### ML Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/cartoon/classify` | Classify a celebrity face in a cartoon image |
| `POST` | `/cartoon/generate` | Generate a cartoon from a real photo using GAN |

### Job Status Values

```
pending  →  processing  →  completed
                        ↘  failed
```

---

## 🤖 ML Models

### Cartoon Generator (GAN)
- Trained using a custom GAN pipeline — see `backend/notebooks/Cartoon_Generator_Training.ipynb`
- Generator + discriminator architecture trained on cartoon face pairs
- Weights stored in `backend/ml_weights/`

### Cartoon Face Classifier
- Classifies cartoon images against **100 public figure identities**
- Training and evaluation in `backend/notebooks/cartoon_model_classify.ipynb`
- CNN-based classifier fine-tuned on cartoon face crops

---

## 🔐 Authentication Flow

```
1. POST /auth/signup    →  { access_token, refresh_token }
2. POST /auth/login/form →  { access_token, refresh_token }
3. All requests         →  Authorization: Bearer <access_token>
4. On 401               →  Clear tokens, redirect to login
```

---

## 🖼️ Image Processing Flow

```
1. Upload    POST /images/upload?style=cartoon       → { job_id }
2. Process   POST /images/{job_id}/process           → status: processing
3. Poll      GET  /images/{job_id}  (every 1s)       → status: completed
4. Display   GET  /images/file/{job_id}/processed    → <img src="...">
5. Download  GET  /images/download/{job_id}          → file download
```

---

## 🧪 Running the Notebooks

The ML training notebooks are in `backend/notebooks/`. Run them in Jupyter or Google Colab:

```bash
pip install jupyter
jupyter notebook backend/notebooks/
```

| Notebook | Purpose |
|---|---|
| `Cartoon_Generator_Training.ipynb` | Full GAN training pipeline |
| `cartoon_model_gen.ipynb` | Generator inference & testing |
| `cartoon_model_classify.ipynb` | Classifier training, eval & confusion matrix |

---

## 🌐 Deployment

### Deploy Backend (Railway / Render / EC2)

1. Set all environment variables from `.env.example` in your hosting dashboard
2. Set `DATABASE_URL` to your production PostgreSQL connection string
3. Start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Run migrations on first deploy:
   ```bash
   alembic upgrade head
   ```

### Deploy Streamlit Frontend (Streamlit Community Cloud)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Point it to `frontend/app.py`
4. Set `BACKEND_URL` secret to your deployed backend URL

### Deploy HTML Frontend (Netlify / Vercel / GitHub Pages)

```bash
# Netlify drag-and-drop or CLI
cd frontend
netlify deploy --dir . --prod
```

Update `js/api.js` to point to your production backend URL before deploying.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI, Uvicorn, Python-Multipart |
| **Auth** | JWT (python-jose), bcrypt, OAuth2 |
| **Database** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **Image Processing** | OpenCV 4.8, Pillow, NumPy |
| **Deep Learning** | PyTorch 2.0, torchvision, SciPy |
| **Frontend (App)** | Streamlit 1.29 |
| **Frontend (Web)** | HTML5, CSS3, Vanilla JavaScript |
| **Storage** | Local filesystem (`storage/uploads`, `storage/processed`) |
| **Rate Limiting** | Custom middleware |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source. See the repository for license details.

---

<div align="center">

**Built with ❤️ by [yuvrajrgv](https://github.com/yuvrajrgv)**

*Toonify AI — Upload a photo. See yourself as a cartoon.*

</div>
