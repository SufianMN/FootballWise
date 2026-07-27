# FootballWise ⚽

![FootballWise Architecture](https://via.placeholder.com/1200x400?text=FootballWise+Banner)

FootballWise is a state-of-the-art predictive analytics and explainable AI platform for football (soccer). Built with a microservices architecture, it leverages historical match data, player statistics, and machine learning to generate highly accurate predictions, comprehensive analytics, and deep tactical insights.

---

## 🌟 Features

- **Predictive Engine**: High-accuracy XGBoost models to predict match outcomes with calibrated confidence scores.
- **Explainable AI (XAI)**: SHAP (SHapley Additive exPlanations) integration that clearly explains *why* the model made a certain prediction, showing feature importances and tactical advantages.
- **Deep Analytics**: Comprehensive team and player statistics, including radar charts for player profiles, form trends, and head-to-head comparisons.
- **Match Explorer**: Detailed timeline events, expected goals (xG), possession stats, and automated AI match summaries.
- **Production-Ready**: fully Dockerized with centralized logging, health checks, and CI/CD pipelines.

---

## 🏗️ Architecture

FootballWise is built with modern, scalable technologies:

### 🚀 Technology Stack
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts & Plotly.js
- **Backend**: Python 3.12, FastAPI, Uvicorn, Pandas, Numpy
- **Machine Learning**: XGBoost, Scikit-learn, SHAP
- **Infrastructure**: Docker, Docker Compose, NGINX, GitHub Actions

### 🧠 ML Pipeline Overview
The machine learning pipeline processes raw Statsbomb event data into highly engineered features:
1. **Data Ingestion**: Parses JSON event data and matches.
2. **Feature Engineering**: Calculates rolling averages, Elo ratings, expected goals (xG), and head-to-head metrics.
3. **Model Training**: Trains an XGBoost classifier with hyperparameter tuning via GridSearchCV.
4. **Explainability**: Fits a SHAP TreeExplainer to the model, producing feature impact values for every prediction.

---

## 📂 Project Structure

```text
FootballWise/
├── client/                 # React Frontend
│   ├── src/                # UI Components, Pages, State Management
│   ├── Dockerfile          # NGINX Multi-stage build
│   └── package.json        # Dependencies
├── server/                 # FastAPI Backend
│   ├── app/                # API Endpoints, Core Logger, ML Services
│   ├── Dockerfile          # Python Uvicorn image
│   └── requirements.txt    # Python dependencies
├── ml/                     # Machine Learning Pipeline
│   ├── data/               # Raw and Processed Datasets
│   ├── models/             # Pickled XGBoost and SHAP artifacts
│   └── scripts/            # Training and dataset building scripts
├── .github/workflows/      # CI/CD Pipelines
└── docker-compose.yml      # Orchestration
```

---

## ⚙️ Setup & Installation

### Option 1: Docker (Recommended)
Run the entire stack using Docker Compose.

```bash
# Clone the repository
git clone https://github.com/SufianMN/FootballWise.git
cd FootballWise

# Build and start the containers
docker compose up --build
```
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000

### Option 2: Local Development

**Backend Setup**
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup**
```bash
cd client
npm install
cp .env.example .env
npm run dev
```

---

## 📚 API Documentation

Once the backend is running, you can access the interactive Swagger documentation at:
`http://localhost:8000/docs`

### Key Endpoints
- `GET /health` - Service health and dataset loading status.
- `POST /predict` - Generate a match prediction and SHAP explanation.
- `GET /team/{id}/analytics` - Deep team tactical analytics.
- `GET /player/{id}` - Comprehensive player profile and radar chart percentiles.

---

## 🚀 Deployment Instructions

### Frontend (Vercel)
1. Import the repository to Vercel.
2. Set the **Framework Preset** to `Vite`.
3. Set the **Root Directory** to `client`.
4. Add the Environment Variable: `VITE_API_URL` pointing to your deployed backend URL.

### Backend (Railway/Render)
1. Connect the repository to Railway/Render.
2. Set the **Root Directory** to `server`.
3. The platform will automatically detect the `server/Dockerfile`.
4. Add the necessary Environment Variables (e.g., `HOST`, `PORT`, `LOG_LEVEL`).
5. Ensure the `ml/` data directory is deployed or accessible if not building a static artifact.

---

## 🔮 Future Improvements
- **Live Data Integration**: Connect to a live football API for real-time match predictions.
- **User Authentication**: Allow users to save their favorite teams and players.
- **Advanced Tactical Maps**: Incorporate pitch heatmaps utilizing the raw coordinate data from Statsbomb.
- **Model Retraining Pipeline**: Automate the ML pipeline to retrain models weekly via GitHub Actions.

---
*Developed by SufianMN*
