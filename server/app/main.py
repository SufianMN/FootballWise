from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from .services.prediction_service import prediction_service
from .services.team_service import team_service
from .services.explainability_service import explainability_service
from .services.analytics_service import analytics_service

app = FastAPI(title="FootballWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("Initializing FootballWise API...")
    prediction_service.load_artifacts()
    team_service.load_data()
    analytics_service.load_data()
    if prediction_service.model is not None:
        explainability_service.initialize(prediction_service.model)
    print("Services successfully loaded.")

class PredictRequest(BaseModel):
    home_team: str
    away_team: str

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "FootballWise API",
        "model_loaded": prediction_service.model is not None
    }

@app.get("/teams")
def get_teams():
    teams = team_service.get_all_teams()
    if not teams:
        raise HTTPException(status_code=500, detail="Failed to load teams")
    return teams

@app.post("/predict")
def predict_match(request: PredictRequest):
    try:
        res = prediction_service.predict(request.home_team, request.away_team)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/team/{team_id}")
def get_team(team_id: str):
    stats = team_service.get_team_stats(team_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Team not found or lacks historical data")
    return stats

@app.get("/team/{team_id}/analytics")
def get_team_analytics(team_id: str):
    data = analytics_service.get_team_analytics(team_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analytics data not found for team")
    return data
