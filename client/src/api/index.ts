import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Default FastAPI URL
});

export const getTeams = () => api.get('/teams');
export const getCompetitions = () => api.get('/competitions');
export const predictMatch = (data: { home_team: string; away_team: string }) => 
  api.post('/predict', data);
export const getTeamStats = (id: string) => api.get(`/team/${id}`);
export const getTeamAnalytics = (id: string) => api.get(`/team/${id}/analytics`);
export const getLeagueAnalytics = (id: string) => api.get(`/league/${id}`);
export const searchMatches = (params: any) => api.get('/matches', { params });
export const getMatchDetails = (id: number) => api.get(`/match/${id}`);

export const getPlayers = () => api.get('/players');
export const getPlayerDetails = (id: number) => api.get(`/player/${id}`);
export const comparePlayers = (p1: number, p2: number) => api.get(`/player/compare?p1=${p1}&p2=${p2}`);

export default api;
