# MediaPulse — Trending Content Analyzer

A comprehensive Python-based data analysis tool for identifying, tracking, and visualizing trending topics across social media platforms. Built with Streamlit for interactive exploration and FastAPI for programmatic access.

## 🎯 Features

- **Multi-Platform Analysis**: Analyze trends across different social media platforms
- **Interactive Dashboard**: Real-time Streamlit UI with filters and visualizations
- **RESTful API**: FastAPI backend for programmatic access to analytics
- **Engagement Metrics**: Track engagement levels, content types, and regional performance
- **Spike Detection**: Automated anomaly detection using z-score analysis
- **Time Series Analysis**: Daily, weekly, and monthly aggregation with moving averages
- **Data Export**: Download filtered and aggregated data as CSV

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │ 
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── mediapulse                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── fetcher.py           <- Scripts to download or generate data
    │   │
    │   ├── processor.py         <- give process data 
    │   │
    │   ├── analysis.py          <- give analysis
    │   │ 
    │   ├── chart.py             <- all the charts.
    │   │ 
    │   ├── api.py               <- api which connect to ui. 
    │   │ 
    │   ├── ui_streamlit.py      <- ui using streamlit library.  
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip or conda
- Docker (optional, for containerization)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AmitZala/MediaPulse---Trending-Content-Analyzer.git
   cd "MediaPulse - Trending Content Analyzer"
   ```

2. **Create and activate virtual environment**

   **On Windows (PowerShell):**
   ```powershell
   python -m venv env
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\env\Scripts\Activate.ps1
   ```

   **On macOS/Linux:**
   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Prepare data**
   - Place your CSV data file in `data/raw/` directory
   - Expected columns: `DateTime`, `Keyword`, `Platform`, `Content_Type`, `Region`, `Engagement_Level`
   - Default file path: `data/raw/Viral_Social_Media_Trends_with_DateTime.csv`

### Running the Project

#### Option 1: Streamlit Dashboard (Recommended)
```bash
streamlit run mediapulse/ui_streamlit.py
```
Access at `http://localhost:8501`

#### Option 2: FastAPI Server
```bash
uvicorn mediapulse.api:app --reload --host 0.0.0.0 --port 8000
```
API docs at `http://localhost:8000/docs`

#### Option 3: Both Services
```bash
# Terminal 1
streamlit run mediapulse/ui_streamlit.py

# Terminal 2
uvicorn mediapulse.api:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t mediapulse:latest .
```

### Run Streamlit
```bash
docker run -p 8501:8501 -v "$(pwd)/data:/app/data" mediapulse:latest
```

### Run FastAPI
```bash
docker run -p 8000:8000 -v "$(pwd)/data:/app/data" mediapulse:latest uvicorn mediapulse.api:app --host 0.0.0.0 --port 8000
```

### Docker Compose
Create `docker-compose.yml` (see docs/docker-compose-template.yml for example)

## 📊 Data Format

Expected CSV columns: `DateTime`, `Keyword`, `Platform`, `Content_Type`, `Region`, `Engagement_Level`

Supported alternate names:
- DateTime: date, time, timestamp
- Keyword: topic, hashtag
- Platform: source, site
- Content_Type: content type, type
- Engagement: engagement_level, likes, shares

## 🔧 Core Modules

- **fetcher.py** - Load CSV data with automatic column detection
- **processor.py** - Clean, aggregate, and filter data
- **analytics.py** - Compute statistics and detect spikes
- **charts.py** - Generate interactive Plotly visualizations
- **api.py** - FastAPI REST endpoints

## 📦 Dependencies

pandas, numpy, streamlit, plotly, fastapi, uvicorn, python-dateutil, matplotlib

## 🧪 Testing

```bash
python test_environment.py
pytest
tox
```

## 📄 License

MIT License

## 👨‍💻 Author

Amit Zala - [@AmitZala](https://github.com/AmitZala)

---

**Last Updated**: December 4, 2025
