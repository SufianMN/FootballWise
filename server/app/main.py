from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from .services.prediction_service import prediction_service
from .services.team_service import team_service
from .services.explainability_service import explainability_service
from .services.analytics_service import analytics_service
from .services.league_service import league_service
from .services.match_service import match_service
from typing import Optional

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
    league_service.load_data()
    match_service.load_data()
    if prediction_service.model is not None:
        explainability_service.initialize(prediction_service.model)
    print("Services successfully loaded.")

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "FootballWise API",
        "model_loaded": prediction_service.model is not None
    }

@app.get("/teams")
def get_teams():
    return team_service.get_all_teams()

@app.get("/competitions")
def get_competitions():
    return league_service.get_competitions()

@app.get("/league/{competition_id}")
def get_league_analytics(competition_id: str):
    data = league_service.get_league_analytics(competition_id)
    if not data:
        raise HTTPException(status_code=404, detail="League data not found")
    return data

@app.get("/matches")
def get_matches(competition: Optional[str] = None, season: Optional[str] = None, team: Optional[str] = None, date: Optional[str] = None, page: int = 1, page_size: int = 20, sort: str = "desc"):
    return match_service.search_matches(competition, season, team, date, page, page_size, sort)

@app.get("/match/{match_id}")
def get_match_details(match_id: int):
    data = match_service.get_match_details(match_id)
    if not data:
        raise HTTPException(status_code=404, detail="Match not found")
    return data

class PredictRequest(BaseModel):
    home_team: str
    away_team: str

@app.post("/predict")
def predict(request: PredictRequest):
    try:
        result = prediction_service.predict(request.home_team, request.away_team)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
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
