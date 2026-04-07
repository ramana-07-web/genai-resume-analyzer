<h1 align="center">🧠 ResumeIQ — AI Resume Analyzer</h1>

<p align="center">
  <strong>Upload a resume. Paste a job description. Get an AI-powered match analysis in seconds.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/flask-3.x-black?logo=flask" alt="Flask" />
  <img src="https://img.shields.io/badge/Gemini_AI-2.5_Flash-orange?logo=google&logoColor=white" alt="Gemini AI" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Smart Resume Parsing** | Dual-engine parser — Affinda API with automatic pypdf fallback |
| 🤖 **Gemini AI Analysis** | Match score, missing skills, strengths, and improvement suggestions |
| 🎨 **Beautiful UI** | Split-screen editorial design with drag-and-drop upload |
| 🔌 **REST API** | JSON endpoint for programmatic integration |
| 🔒 **Privacy First** | Files are processed in-memory and deleted immediately |
| 🚀 **Deploy Anywhere** | Heroku, Render, Railway, Docker — ready out of the box |

---

## 📸 Screenshots

<table>
  <tr>
    <td align="center"><b>Upload Page</b></td>
    <td align="center"><b>Analysis Result</b></td>
  </tr>
  <tr>
    <td><img src="https://via.placeholder.com/400x300?text=Upload+Page" alt="Upload Page" /></td>
    <td><img src="https://via.placeholder.com/400x300?text=Analysis+Result" alt="Analysis Result" /></td>
  </tr>
</table>

> 💡 *Replace the placeholder images above with actual screenshots of your deployed app.*

---

## 🏗️ Architecture

```
genai-resume-analyzer/
├── app.py                  # Flask application (routes & logic)
├── utils/
│   ├── __init__.py
│   ├── affinda_parser.py   # Affinda API + pypdf fallback parser
│   └── gemini_llm.py       # Gemini AI analysis engine
├── templates/
│   └── index.html          # Frontend UI
├── temp/                   # Temporary upload directory (auto-cleaned)
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku/Railway deployment
├── Dockerfile              # Container deployment
├── render.yaml             # Render.com one-click deploy
├── runtime.txt             # Python version spec
├── .env.example            # Environment variable template
├── .gitignore
└── LICENSE
```

### How It Works

```
PDF Upload → Resume Parser → Structured Data → Gemini AI → Analysis Report
                  │                                             │
          Affinda API (primary)                          Match Score
          pypdf (fallback)                              Missing Skills
                                                        Strengths
                                                        Suggestions
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed
- A **Gemini API key** (free) — [Get one here](https://aistudio.google.com/apikey)
- *(Optional)* An **Affinda API key** — [Sign up here](https://api.affinda.com/)

### 1. Clone the repository

```bash
git clone https://github.com/ramana-07-web/genai-resume-analyzer.git
cd genai-resume-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here

# Optional — if not set, pypdf is used as fallback
AFFINDA_API_KEY=your_affinda_key
AFFINDA_WORKSPACE=your_workspace_id
```

### 5. Run the application

```bash
python app.py
```

Open **http://localhost:5000/ui** in your browser.

---

## 🔌 API Reference

### `POST /analyze`

Programmatic JSON endpoint for resume analysis.

**Request** (multipart/form-data):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume` | File (PDF) | ✅ | Resume PDF file |
| `job_desc` | String | ✅ | Job description text |

**Example with cURL:**

```bash
curl -X POST http://localhost:5000/analyze \
  -F "resume=@path/to/resume.pdf" \
  -F "job_desc=Looking for a Python developer with 3+ years experience..."
```

**Response:**

```json
{
  "parsed_data": {
    "name": "John Doe",
    "skills": ["Python", "Flask", "React"],
    "education": ["B.Tech Computer Science"],
    "experience": ["Software Engineer at XYZ"]
  },
  "analysis": "Match Score: 72\n\nMissing Skills:\n- Kubernetes\n...",
  "parse_source": "pypdf_fallback",
  "analysis_source": "Gemini"
}
```

### `POST /analyze-ui`

Browser-based endpoint — returns a styled HTML results page. Used internally by the upload form at `/ui`.

---

## ☁️ Deployment

### Option 1: Render (Recommended — Free Tier)

1. Push your repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo — Render auto-detects `render.yaml`
4. Add your API keys in **Environment Variables**
5. Click **Deploy** 🚀

### Option 2: Heroku

```bash
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

### Option 3: Railway

1. Go to [railway.app](https://railway.app) → **New Project from GitHub**
2. Add environment variables in the dashboard
3. Railway auto-detects the `Procfile`

### Option 4: Docker

```bash
# Build the image
docker build -t resumeiq .

# Run the container
docker run -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  -e AFFINDA_API_KEY=your_key \
  -e AFFINDA_WORKSPACE=your_workspace \
  resumeiq
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask |
| **AI Engine** | Google Gemini 2.5 Flash |
| **Resume Parsing** | Affinda v3 API + pypdf fallback |
| **Frontend** | Vanilla HTML/CSS/JS with editorial design |
| **Production Server** | Gunicorn |
| **Deployment** | Docker, Heroku, Render, Railway |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Google Gemini AI](https://ai.google.dev/) — for the powerful LLM analysis engine
- [Affinda](https://www.affinda.com/) — for the enterprise-grade resume parser
- [pypdf](https://github.com/py-pdf/pypdf) — for the reliable offline PDF parser

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/ramana-07-web">Dharmapuri Venkata Ramana</a>
</p>
