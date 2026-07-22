from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="FootballWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    competition: str
    season: str

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "FootballWise API"
    }

@app.get("/teams")
def get_teams():
    return [
        {"id": "t1", "name": "Arsenal"},
        {"id": "t2", "name": "Manchester City"},
        {"id": "t3", "name": "Real Madrid"},
        {"id": "t4", "name": "Barcelona"}
    ]

@app.get("/competitions")
def get_competitions():
    return [
        {"id": "c1", "name": "Premier League"},
        {"id": "c2", "name": "La Liga"},
        {"id": "c3", "name": "Champions League"}
    ]

@app.post("/predict")
def predict_match(request: PredictRequest):
    return {
        "home_win_probability": 0.61,
        "draw_probability": 0.22,
        "away_win_probability": 0.17,
        "predicted_score": "2-1"
    }

@app.get("/team/{team_id}")
def get_team(team_id: str):
    # Mock statistics
    return {
        "id": team_id,
        "goals": 45,
        "xg": 42.5,
        "possession": 55.2,
        "passing_accuracy": 88.4,
        "defensive_rating": 7.5,
        "recent_form": ["W", "D", "W", "W", "L"],
        "shots": 210,
        "pressing": 45.3
    }
