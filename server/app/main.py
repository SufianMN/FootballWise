from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import traceback

from .services.team_service import team_service
from .services.prediction_service import prediction_service
from .services.explainability_service import explainability_service
from .services.league_service import league_service
from .services.match_service import match_service
from .services.player_service import player_service
from .utils.helpers import convert_numpy_types

app = FastAPI(title="FootballWise API")

# Add CORS middleware to allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load all necessary data when the server starts."""
    team_service.load_data()
    league_service.load_data()
    match_service.load_data()
    player_service.load_data()
    prediction_service.load_model()
    if prediction_service.model is not None:
        explainability_service.initialize(prediction_service.model)

@app.get("/")
def read_root():
    return {"message": "Welcome to FootballWise API"}

# --- Team Endpoints ---

@app.get("/teams")
def get_teams():
    """Return a list of all available teams."""
    teams = team_service.get_all_teams()
    return {"data": convert_numpy_types(teams)}

@app.get("/team/{team_id}")
def get_team_stats(team_id: str):
    """Return historical statistics for a specific team."""
    stats = team_service.get_team_stats(team_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"data": convert_numpy_types(stats)}

@app.get("/team/{team_id}/analytics")
def get_team_analytics(team_id: str):
    """Return detailed analytics for a team (trends, home vs away, discipline)."""
    analytics = team_service.get_team_analytics(team_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Team analytics not found")
    return {"data": convert_numpy_types(analytics)}

# --- League Endpoints ---

@app.get("/competitions")
def get_competitions():
    """Return a list of all available competitions."""
    competitions = league_service.get_competitions()
    return {"data": convert_numpy_types(competitions)}

@app.get("/league/{competition_id}")
def get_league_analytics(competition_id: str):
    """Return league tables and statistical leaders for a given competition."""
    analytics = league_service.get_league_analytics(competition_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Competition not found")
    return {"data": convert_numpy_types(analytics)}

# --- Match Endpoints ---

@app.get("/matches")
def get_matches(
    team: Optional[str] = None,
    competition: Optional[str] = None,
    season: Optional[str] = None,
    date: Optional[str] = None,
    sort: Optional[str] = "desc",
    page: int = 1,
    page_size: int = 20
):
    """Return a paginated, filtered list of historical matches."""
    result = match_service.search_matches(
        team=team, 
        competition=competition, 
        season=season, 
        date=date, 
        sort=sort, 
        page=page, 
        page_size=page_size
    )
    return {"data": convert_numpy_types(result)}

@app.get("/match/{match_id}")
def get_match_details(match_id: int):
    """Return detailed stats, timeline events, and a summary for a specific match."""
    details = match_service.get_match_details(match_id)
    if not details:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"data": convert_numpy_types(details)}

# --- Player Endpoints ---

@app.get("/players")
def get_players():
    """Return a list of all available players."""
    players = player_service.get_players()
    return {"data": convert_numpy_types(players)}

@app.get("/player/compare")
def compare_players(p1: int, p2: int):
    """Return side-by-side comparison of two players."""
    comparison = player_service.compare_players(p1, p2)
    return {"data": convert_numpy_types(comparison)}

@app.get("/player/{player_id}")
def get_player_details(player_id: int):
    """Return comprehensive stats for a specific player."""
    details = player_service.get_player_details(player_id)
    if not details:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"data": convert_numpy_types(details)}

# --- Prediction Endpoints ---

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str

@app.post("/predict")
def predict(request: PredictionRequest):
    """Generate a match prediction with confidence scores and top features."""
    try:
        prediction = prediction_service.predict(request.home_team, request.away_team)
        return {"data": convert_numpy_types(prediction)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred during prediction.")
