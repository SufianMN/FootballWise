import { create } from 'zustand';

interface AppState {
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  selectedHomeTeam: string | null;
  selectedAwayTeam: string | null;
  setSelectedTeams: (home: string, away: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: 'dark',
  setTheme: (theme) => set({ theme }),
  selectedHomeTeam: null,
  selectedAwayTeam: null,
  setSelectedTeams: (home, away) => set({ selectedHomeTeam: home, selectedAwayTeam: away }),
}));
