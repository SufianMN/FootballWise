import React, { useState, useEffect } from 'react';
import { getTeams, predictMatch } from '../api';
import SearchableTeamSelect from '../components/SearchableTeamSelect/SearchableTeamSelect';
import { Activity, Sparkles, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';

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
    confidenceLevel: string;
    matchPreview: any;
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
    if (!homeTeam || !awayTeam) return;
    if (homeTeam === awayTeam) {
      setError("Home and Away teams must be different.");
      setPrediction(null);
      return;
    }
    
    setError(null);
    setLoading(true);
    
    try {
      const response = await predictMatch({ home_team: homeTeam, away_team: awayTeam });
      const data = response.data.data;
      
      setPrediction({
        homeWin: Math.round(data.home_win_probability * 100),
        draw: Math.round(data.draw_probability * 100),
        awayWin: Math.round(data.away_win_probability * 100),
        result: data.predicted_result,
        confidence: data.confidence,
        confidenceLevel: data.confidence_level,
        matchPreview: data.match_preview,
        top_features: data.top_features || [],
        insights: data.insights || []
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred during prediction.");
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (homeTeam && awayTeam && homeTeam !== awayTeam) {
      handlePredict();
    }
  }, [homeTeam, awayTeam]);

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 sm:px-6">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
          <Activity size={28} />
        </div>
        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
            Match Prediction
          </h2>
          <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">XGBoost ML Probability Engine</p>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-950/80 border border-red-500/50 text-red-200 px-5 py-4 rounded-xl mb-6 shadow-xl flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Team Selector Panel */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 sm:p-8 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 mb-8 relative z-30">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-slate-300 font-semibold text-sm mb-2">Home Team</label>
            <SearchableTeamSelect 
              teams={teams}
              value={homeTeam}
              onChange={(id) => setHomeTeam(id)}
              placeholder="Search home team..."
            />
          </div>
          <div>
            <label className="block text-slate-300 font-semibold text-sm mb-2">Away Team</label>
            <SearchableTeamSelect 
              teams={teams}
              value={awayTeam}
              onChange={(id) => setAwayTeam(id)}
              placeholder="Search away team..."
            />
          </div>
        </div>
        {loading && (
          <div className="w-full bg-gradient-to-r from-blue-600/20 to-indigo-600/20 border border-blue-500/30 text-blue-300 py-4 rounded-xl flex items-center justify-center gap-3 font-semibold shadow-inner">
            <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            <span>Analyzing Tactical Matchup & Computing Probabilities...</span>
          </div>
        )}
      </div>

      {prediction && (
        <div className="space-y-6 animate-fade-in">
          
          {/* Match Preview Section */}
          <div className="bg-slate-900/90 backdrop-blur-md p-6 sm:p-8 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40">
            <h4 className="text-lg font-bold text-slate-100 mb-6 border-b border-slate-700/80 pb-3 flex items-center gap-2">
              <TrendingUp size={20} className="text-indigo-400" />
              <span>Match Preview (Last 5 Matches)</span>
            </h4>
            
            <div className="grid grid-cols-3 text-center gap-4 mb-6 items-center">
              <div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Home Form</div>
                <div className="font-mono text-xl font-bold tracking-widest text-emerald-400">{prediction.matchPreview.home_form}</div>
              </div>
              <div className="text-slate-600 font-black text-xl">VS</div>
              <div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Away Form</div>
                <div className="font-mono text-xl font-bold tracking-widest text-blue-400">{prediction.matchPreview.away_form}</div>
              </div>
            </div>

            <div className="space-y-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
              <div className="grid grid-cols-3 text-center items-center">
                <div className="text-xl font-extrabold text-white">{prediction.matchPreview.home_avg_goals}</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider">Avg Goals</div>
                <div className="text-xl font-extrabold text-white">{prediction.matchPreview.away_avg_goals}</div>
              </div>
              
              <div className="grid grid-cols-3 text-center items-center">
                <div className="text-xl font-extrabold text-slate-300">{prediction.matchPreview.home_avg_xg}</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider">Expected Goals (xG)</div>
                <div className="text-xl font-extrabold text-slate-300">{prediction.matchPreview.away_avg_xg}</div>
              </div>
              
              <div className="grid grid-cols-3 text-center items-center">
                <div className="text-xl font-extrabold text-emerald-400">{prediction.matchPreview.home_clean_sheets}</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider">Clean Sheets</div>
                <div className="text-xl font-extrabold text-emerald-400">{prediction.matchPreview.away_clean_sheets}</div>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-slate-800 grid grid-cols-3 text-center items-center">
              <div className="text-2xl font-black text-blue-400">{prediction.matchPreview.h2h_home_wins}</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider">Head-to-Head Wins</div>
              <div className="text-2xl font-black text-red-400">{prediction.matchPreview.h2h_away_wins}</div>
            </div>
          </div>

          {/* Main Prediction Card */}
          <div className="bg-slate-900/90 backdrop-blur-md p-8 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 relative overflow-hidden">
            <div className={`absolute top-0 right-0 px-4 py-1.5 rounded-bl-xl font-bold text-xs border-b border-l uppercase tracking-wider
              ${prediction.confidenceLevel === 'Very High' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 
                prediction.confidenceLevel === 'High' ? 'bg-blue-500/20 text-blue-300 border-blue-500/40' : 
                prediction.confidenceLevel === 'Medium' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40' : 
                'bg-red-500/20 text-red-300 border-red-500/40'}`}>
              {prediction.confidence}% Confidence ({prediction.confidenceLevel})
            </div>
            
            <h3 className="text-xl font-bold mb-8 text-center text-slate-300">Prediction Results</h3>
            
            <div className="text-center mb-10">
              <div className="text-slate-400 mb-2 uppercase tracking-widest text-xs font-semibold">Predicted Outcome</div>
              <div className="text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400">
                {prediction.result}
              </div>
            </div>

            <div className="space-y-6">
              {/* Home Win Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-200 font-semibold">Home Win</span>
                  <span className="text-blue-400 font-bold">{prediction.homeWin}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-3.5 overflow-hidden border border-slate-800">
                  <div 
                    className="bg-gradient-to-r from-blue-600 to-blue-400 h-3.5 rounded-full transition-all duration-1000 ease-out shadow-md shadow-blue-500/20" 
                    style={{ width: `${prediction.homeWin}%` }}
                  ></div>
                </div>
              </div>

              {/* Draw Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-200 font-semibold">Draw</span>
                  <span className="text-slate-400 font-bold">{prediction.draw}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-3.5 overflow-hidden border border-slate-800">
                  <div 
                    className="bg-gradient-to-r from-slate-600 to-slate-400 h-3.5 rounded-full transition-all duration-1000 ease-out" 
                    style={{ width: `${prediction.draw}%` }}
                  ></div>
                </div>
              </div>

              {/* Away Win Bar */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-200 font-semibold">Away Win</span>
                  <span className="text-emerald-400 font-bold">{prediction.awayWin}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-3.5 overflow-hidden border border-slate-800">
                  <div 
                    className="bg-gradient-to-r from-emerald-600 to-emerald-400 h-3.5 rounded-full transition-all duration-1000 ease-out shadow-md shadow-emerald-500/20" 
                    style={{ width: `${prediction.awayWin}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Why This Prediction? */}
            <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40">
              <h4 className="text-lg font-bold text-slate-100 mb-4 border-b border-slate-800 pb-3 flex items-center gap-2">
                <CheckCircle size={20} className="text-emerald-400" />
                <span>Why This Prediction?</span>
              </h4>
              <ul className="space-y-4">
                {prediction.insights.map((insight, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <div className="mt-1 flex-shrink-0 bg-emerald-500/20 text-emerald-400 rounded-full p-1 border border-emerald-500/30">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <span className="text-slate-300 text-sm sm:text-base">{insight}</span>
                  </li>
                ))}
                {prediction.insights.length === 0 && (
                  <li className="text-slate-500 italic">No specific insights generated.</li>
                )}
              </ul>
            </div>

            {/* Prediction Factors */}
            <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40">
              <h4 className="text-lg font-bold text-slate-100 mb-4 border-b border-slate-800 pb-3 flex items-center gap-2">
                <Sparkles size={20} className="text-indigo-400" />
                <span>SHAP Prediction Factors</span>
              </h4>
              <div className="space-y-3">
                {prediction.top_features.map((feature, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <div className="flex items-center gap-2">
                      {feature.direction === 'positive' && <span className="text-emerald-400 font-bold">⬆</span>}
                      {feature.direction === 'negative' && <span className="text-red-400 font-bold">⬇</span>}
                      {feature.direction === 'neutral' && <span className="text-slate-400 font-bold">▪</span>}
                      <span className="text-slate-300 font-medium text-sm">{feature.feature}</span>
                    </div>
                    <div className={`font-mono font-bold text-sm ${feature.direction === 'positive' ? 'text-emerald-400' : feature.direction === 'negative' ? 'text-red-400' : 'text-slate-400'}`}>
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

