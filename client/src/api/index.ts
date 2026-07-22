import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Default FastAPI URL
});

export const getTeams = () => api.get('/teams');
export const getCompetitions = () => api.get('/competitions');
export const predictMatch = (data: { home_team: string; away_team: string; competition: string; season: string }) => 
  api.post('/predict', data);
export const getTeamStats = (id: string) => api.get(`/team/${id}`);

export default api;
