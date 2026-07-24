import React, { useState, useEffect } from 'react';
import { getTeams, predictMatch } from '../api';
import SearchableTeamSelect from '../components/SearchableTeamSelect/SearchableTeamSelect';

const PredictionPage: React.FC = () => {
  const [teams, setTeams] = useState<{ id: string; name: string }[]>([]);
  const [homeTeam, setHomeTeam] = useState<string>('');
  const [awayTeam, setAwayTeam] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [prediction, setPrediction] = useState<{
    homeWin: number; 
    draw: number; 
    awayWin: number;
    result: string;
    confidence: number;
    top_features: { feature: string; value: number; impact: number; direction: 'positive' | 'negative' | 'neutral' }[];
    insights: string[];
  } | null>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await getTeams();
        setTeams(response.data.data);
        if (response.data.data.length >= 2) {
          setHomeTeam(response.data.data[0].id);
          setAwayTeam(response.data.data[1].id);
        }
      } catch (err) {
        console.error("Failed to load teams:", err);
        setError("Failed to load teams from the server.");
      }
    };
    fetchTeams();
  }, []);

  const handlePredict = async () => {
    if (homeTeam === awayTeam) {
      setError("Home and Away teams must be different.");
      return;
    }
    
    setError(null);
    setLoading(true);
    setPrediction(null);
    
    try {
      const response = await predictMatch({ home_team: homeTeam, away_team: awayTeam });
      const data = response.data.data;
      
      setPrediction({
        homeWin: Math.round(data.home_win_probability * 100),
        draw: Math.round(data.draw_probability * 100),
        awayWin: Math.round(data.away_win_probability * 100),
        result: data.predicted_result,
        confidence: data.confidence,
        top_features: data.top_features || [],
        insights: data.insights || []
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred during prediction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h2 className="text-3xl font-bold mb-8 text-white">Match Prediction</h2>
      
      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div className="bg-surface p-6 rounded-xl border border-slate-700 mb-8 shadow-lg">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-textSecondary mb-2">Home Team</label>
            <SearchableTeamSelect 
              teams={teams}
              value={homeTeam}
              onChange={(id) => setHomeTeam(id)}
              placeholder="Search home team..."
            />
          </div>
          <div>
            <label className="block text-textSecondary mb-2">Away Team</label>
            <SearchableTeamSelect 
              teams={teams}
              value={awayTeam}
              onChange={(id) => setAwayTeam(id)}
              placeholder="Search away team..."
            />
          </div>
        </div>
        <button 
          onClick={handlePredict}
          disabled={loading || teams.length === 0}
          className="w-full bg-primary hover:bg-blue-600 disabled:bg-slate-600 text-white font-bold py-4 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Analyzing Matchup...
            </>
          ) : "Generate Prediction"}
        </button>
      </div>

      {prediction && (
        <div className="space-y-6 animate-fade-in">
          {/* Main Prediction Card */}
          <div className="bg-surface p-8 rounded-xl border border-slate-700 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-primary/20 text-primary px-4 py-1 rounded-bl-lg font-semibold text-sm border-b border-l border-primary/30">
              {prediction.confidence}% Confidence
            </div>
            
            <h3 className="text-xl font-bold mb-8 text-center text-slate-300">Prediction Results</h3>
            
            <div className="text-center mb-10">
              <div className="text-textSecondary mb-2 uppercase tracking-widest text-sm">Predicted Outcome</div>
              <div className="text-5xl font-extrabold text-white bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                {prediction.result}
              </div>
            </div>

            <div className="space-y-6">
              {/* Home Win Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-white font-medium">Home Win</span>
                  <span className="text-blue-400 font-bold">{prediction.homeWin}%</span>
                </div>
                <div className="w-full bg-background rounded-full h-3 overflow-hidden border border-slate-700">
                  <div 
                    className="bg-blue-500 h-3 rounded-full transition-all duration-1000 ease-out" 
                    style={{ width: `${prediction.homeWin}%` }}
                  ></div>
                </div>
              </div>

              {/* Draw Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-white font-medium">Draw</span>
                  <span className="text-slate-400 font-bold">{prediction.draw}%</span>
                </div>
                <div className="w-full bg-background rounded-full h-3 overflow-hidden border border-slate-700">
                  <div 
                    className="bg-slate-500 h-3 rounded-full transition-all duration-1000 ease-out" 
                    style={{ width: `${prediction.draw}%` }}
                  ></div>
                </div>
              </div>

              {/* Away Win Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-white font-medium">Away Win</span>
                  <span className="text-emerald-400 font-bold">{prediction.awayWin}%</span>
                </div>
                <div className="w-full bg-background rounded-full h-3 overflow-hidden border border-slate-700">
                  <div 
                    className="bg-emerald-500 h-3 rounded-full transition-all duration-1000 ease-out" 
                    style={{ width: `${prediction.awayWin}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Why This Prediction? */}
            <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-xl">
              <h4 className="text-lg font-bold text-white mb-4 border-b border-slate-600 pb-2">Why This Prediction?</h4>
              <ul className="space-y-4">
                {prediction.insights.map((insight, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <div className="mt-1 flex-shrink-0 bg-emerald-500/20 text-emerald-400 rounded-full p-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <span className="text-slate-300">{insight}</span>
                  </li>
                ))}
                {prediction.insights.length === 0 && (
                  <li className="text-slate-500 italic">No specific insights generated.</li>
                )}
              </ul>
            </div>

            {/* Prediction Factors */}
            <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-xl">
              <h4 className="text-lg font-bold text-white mb-4 border-b border-slate-600 pb-2">Prediction Factors</h4>
              <div className="space-y-3">
                {prediction.top_features.map((feature, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-background p-3 rounded-lg border border-slate-700/50">
                    <div className="flex items-center gap-2">
                      {feature.direction === 'positive' && <span className="text-emerald-500 font-bold">⬆</span>}
                      {feature.direction === 'negative' && <span className="text-red-500 font-bold">⬇</span>}
                      {feature.direction === 'neutral' && <span className="text-slate-400 font-bold">▪</span>}
                      <span className="text-slate-300 font-medium text-sm">{feature.feature}</span>
                    </div>
                    <div className={`font-mono font-bold ${feature.direction === 'positive' ? 'text-emerald-400' : feature.direction === 'negative' ? 'text-red-400' : 'text-slate-400'}`}>
                      {feature.impact > 0 ? '+' : ''}{feature.impact.toFixed(2)}
                    </div>
                  </div>
                ))}
                {prediction.top_features.length === 0 && (
                  <div className="text-slate-500 italic">No features returned.</div>
                )}
              </div>
            </div>
          </div>
          
        </div>
      )}
    </div>
  );
};

export default PredictionPage;
