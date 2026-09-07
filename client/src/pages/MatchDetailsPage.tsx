import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMatchDetails } from '../api';
import { ChevronLeft, Calendar, Clock, Trophy, AlertCircle } from 'lucide-react';

const MatchDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [matchData, setMatchData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchMatch = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const res = await getMatchDetails(parseInt(id));
        setMatchData(res.data.data);
      } catch (err) {
        console.error("Failed to load match details:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMatch();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-12 px-4 space-y-8">
        <div className="h-64 bg-slate-900/80 border border-slate-700/80 rounded-2xl animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-96 bg-slate-900/80 border border-slate-700/80 rounded-2xl animate-pulse"></div>
          <div className="h-96 bg-slate-900/80 border border-slate-700/80 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (!matchData) {
    return (
      <div className="max-w-5xl mx-auto py-20 px-4 text-center">
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-12 max-w-lg mx-auto">
          <AlertCircle size={56} className="mx-auto text-red-400 mb-4" />
          <h2 className="text-3xl font-extrabold text-white mb-2">Match Not Found</h2>
          <p className="text-slate-400 mb-6">We couldn't find the details for this match.</p>
          <button 
            onClick={() => navigate('/matches')} 
            className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20 transition-all"
          >
            Back to Matches
          </button>
        </div>
      </div>
    );
  }

  const { home_team, away_team, score, date, competition, season, statistics, events, summary } = matchData;

  const StatComparison = ({ label, homeVal, awayVal, isPercentage = false }: any) => {
    const total = homeVal + awayVal;
    let homePct = total > 0 ? (homeVal / total) * 100 : 50;
    let awayPct = total > 0 ? (awayVal / total) * 100 : 50;
    
    if (isPercentage) {
      homePct = homeVal;
      awayPct = awayVal;
    }

    return (
      <div className="mb-6">
        <div className="flex justify-between text-sm mb-2 font-medium">
          <span className={`font-bold ${homeVal >= awayVal ? 'text-blue-400' : 'text-slate-400'}`}>
            {homeVal}{isPercentage ? '%' : ''}
          </span>
          <span className="text-slate-400 uppercase tracking-wider text-xs font-bold">{label}</span>
          <span className={`font-bold ${awayVal >= homeVal ? 'text-red-400' : 'text-slate-400'}`}>
            {awayVal}{isPercentage ? '%' : ''}
          </span>
        </div>
        <div className="flex h-2.5 rounded-full overflow-hidden bg-slate-950/80 border border-slate-700/50">
          <div className="bg-gradient-to-r from-blue-600 to-cyan-500 h-full transition-all" style={{ width: `${homePct}%` }}></div>
          <div className="bg-gradient-to-r from-rose-500 to-red-600 h-full transition-all" style={{ width: `${awayPct}%` }}></div>
        </div>
      </div>
    );
  };

  const getEventIcon = (type: string) => {
    if (type.includes('Goal') && !type.includes('Missed')) return '⚽';
    if (type.includes('Yellow Card')) return '🟨';
    if (type.includes('Red Card')) return '🟥';
    if (type.includes('Substitution')) return '🔄';
    if (type.includes('Missed')) return '❌';
    return '🔹';
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 animate-fade-in relative">
      {/* Background radial glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/15 blur-3xl rounded-full pointer-events-none"></div>

      <button 
        onClick={() => navigate('/matches')}
        className="flex items-center gap-2 px-4 py-2 bg-slate-900/80 backdrop-blur-md border border-slate-700/80 rounded-xl text-slate-300 hover:text-white hover:border-slate-600 mb-6 transition-all text-sm font-semibold shadow-md"
      >
        <ChevronLeft size={18} /> Back to Matches
      </button>

      {/* HEADER / SCOREBOARD */}
      <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-8 mb-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-indigo-600/10 rounded-full blur-3xl -ml-32 -mb-32 pointer-events-none"></div>

        <div className="flex justify-center items-center gap-2 text-sm text-slate-400 mb-6 font-medium relative z-10">
          <Trophy size={16} className="text-amber-400" />
          <span className="text-slate-200 font-semibold">{competition} &bull; {season}</span>
          <span className="mx-2 text-slate-600">|</span>
          <Calendar size={16} className="text-indigo-400" />
          <span>{date}</span>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-8 relative z-10">
          <div className="flex-1 text-center md:text-right">
            <h2 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white mb-1">
              {home_team}
            </h2>
            <div className="text-xs uppercase font-bold tracking-widest text-slate-400">Home</div>
          </div>
          
          <div className="flex flex-col items-center justify-center">
            <div className="flex items-center gap-4 bg-slate-950/90 border border-slate-700 px-8 py-4 rounded-2xl shadow-inner shadow-black/50">
              <span className="text-5xl font-black text-white">{score.home}</span>
              <span className="text-2xl text-slate-600">-</span>
              <span className="text-5xl font-black text-white">{score.away}</span>
            </div>
            <div className="mt-4 text-xs font-bold text-indigo-300 uppercase tracking-widest bg-gradient-to-r from-indigo-500/20 to-purple-500/20 px-4 py-1 rounded-full border border-indigo-500/40">
              Full Time
            </div>
          </div>

          <div className="flex-1 text-center md:text-left">
            <h2 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-indigo-400 mb-1">
              {away_team}
            </h2>
            <div className="text-xs uppercase font-bold tracking-widest text-slate-400">Away</div>
          </div>
        </div>
      </div>

      {/* MATCH SUMMARY */}
      {summary && (
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-6 mb-8 relative overflow-hidden">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/30 shrink-0">
              <ActivityIcon />
            </div>
            <div>
              <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-200 mb-2">
                Match Insights
              </h3>
              <p className="text-slate-300 leading-relaxed text-sm">{summary}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* STATISTICS COMPARISON */}
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChartIcon /> Team Statistics
          </h3>
          <div className="space-y-6">
            <StatComparison label="Possession" homeVal={statistics.home.possession} awayVal={statistics.away.possession} isPercentage={true} />
            <StatComparison label="Expected Goals (xG)" homeVal={statistics.home.xg} awayVal={statistics.away.xg} />
            <StatComparison label="Total Shots" homeVal={statistics.home.shots} awayVal={statistics.away.shots} />
            <StatComparison label="Shots on Target" homeVal={statistics.home.shots_on_target} awayVal={statistics.away.shots_on_target} />
            <StatComparison label="Pass Accuracy" homeVal={statistics.home.pass_accuracy} awayVal={statistics.away.pass_accuracy} isPercentage={true} />
            <StatComparison label="Corners" homeVal={statistics.home.corners} awayVal={statistics.away.corners} />
            <StatComparison label="Yellow Cards" homeVal={statistics.home.yellow_cards} awayVal={statistics.away.yellow_cards} />
            <StatComparison label="Red Cards" homeVal={statistics.home.red_cards} awayVal={statistics.away.red_cards} />
          </div>
        </div>

        {/* EVENT TIMELINE */}
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-6 flex flex-col max-h-[700px]">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Clock size={20} className="text-indigo-400" /> Match Events
          </h3>
          
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {events && events.length > 0 ? (
              <div className="relative border-l-2 border-slate-700/80 ml-4 pl-6 pb-4 space-y-6">
                {events.map((ev: any, idx: number) => {
                  const isHome = ev.team === home_team;
                  return (
                    <div key={idx} className="relative">
                      {/* Timeline Dot */}
                      <div className="absolute -left-[35px] w-8 h-8 bg-slate-900 border border-slate-700 rounded-full flex items-center justify-center text-sm shadow-md">
                        {getEventIcon(ev.type)}
                      </div>
                      
                      <div className={`flex flex-col bg-slate-950/70 rounded-xl p-3 border border-slate-700/50 ${isHome ? 'border-l-blue-500 border-l-4' : 'border-l-rose-500 border-l-4'}`}>
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-extrabold text-white text-sm">{ev.minute}'</span>
                          <span className="text-xs text-indigo-300 uppercase font-bold tracking-wider">{ev.type}</span>
                        </div>
                        <div className="text-sm font-semibold text-slate-200">{ev.player}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{ev.team}</div>
                        {ev.type === 'Substitution' && (
                          <div className="text-xs text-slate-400 italic mt-1">{ev.description}</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 italic border-2 border-dashed border-slate-700/80 rounded-xl">
                Detailed event data is not available for this match.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Quick helper icons
const ActivityIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>;
const BarChartIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>;

export default MatchDetailsPage;
