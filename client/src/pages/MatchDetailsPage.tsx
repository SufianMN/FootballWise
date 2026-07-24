import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMatchDetails } from '../api';
import { ChevronLeft, Calendar, MapPin, Clock, Trophy, AlertCircle } from 'lucide-react';

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
        setMatchData(res.data);
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
      <div className="max-w-5xl mx-auto py-8 px-4">
        <div className="h-64 bg-surface rounded-xl animate-pulse mb-8"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-96 bg-surface rounded-xl animate-pulse"></div>
          <div className="h-96 bg-surface rounded-xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (!matchData) {
    return (
      <div className="max-w-5xl mx-auto py-20 px-4 text-center">
        <AlertCircle size={48} className="mx-auto text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Match Not Found</h2>
        <p className="text-textSecondary mb-6">We couldn't find the details for this match.</p>
        <button onClick={() => navigate('/matches')} className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors">
          Back to Matches
        </button>
      </div>
    );
  }

  const { home_team, away_team, score, date, competition, season, statistics, events, summary } = matchData;

  const StatComparison = ({ label, homeVal, awayVal, isPercentage = false }: any) => {
    const total = homeVal + awayVal;
    let homePct = total > 0 ? (homeVal / total) * 100 : 50;
    let awayPct = total > 0 ? (awayVal / total) * 100 : 50;
    
    // For things like possession that are already percentages
    if (isPercentage) {
      homePct = homeVal;
      awayPct = awayVal;
    }

    return (
      <div className="mb-6">
        <div className="flex justify-between text-sm mb-2">
          <span className={`font-bold ${homeVal >= awayVal ? 'text-white' : 'text-slate-400'}`}>
            {homeVal}{isPercentage ? '%' : ''}
          </span>
          <span className="text-textSecondary uppercase tracking-wider text-xs font-bold">{label}</span>
          <span className={`font-bold ${awayVal >= homeVal ? 'text-white' : 'text-slate-400'}`}>
            {awayVal}{isPercentage ? '%' : ''}
          </span>
        </div>
        <div className="flex h-2 rounded-full overflow-hidden bg-slate-800">
          <div className="bg-blue-500 h-full" style={{ width: `${homePct}%` }}></div>
          <div className="bg-red-500 h-full" style={{ width: `${awayPct}%` }}></div>
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
    <div className="max-w-5xl mx-auto py-8 px-4 animate-fade-in">
      <button 
        onClick={() => navigate('/matches')}
        className="flex items-center gap-2 text-textSecondary hover:text-white mb-6 transition-colors"
      >
        <ChevronLeft size={18} /> Back to Matches
      </button>

      {/* HEADER / SCOREBOARD */}
      <div className="bg-surface rounded-2xl border border-slate-700 shadow-2xl p-8 mb-8 relative overflow-hidden">
        {/* Abstract Background Element */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl -ml-32 -mb-32"></div>

        <div className="flex justify-center items-center gap-2 text-sm text-textSecondary mb-6 font-medium relative z-10">
          <Trophy size={16} className="text-yellow-500" />
          <span>{competition} &bull; {season}</span>
          <span className="mx-2">|</span>
          <Calendar size={16} />
          <span>{date}</span>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-8 relative z-10">
          <div className="flex-1 text-center md:text-right">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">{home_team}</h2>
            <div className="text-sm text-slate-400">Home</div>
          </div>
          
          <div className="flex flex-col items-center justify-center">
            <div className="flex items-center gap-4 bg-slate-900 border border-slate-700 px-8 py-4 rounded-2xl shadow-inner">
              <span className="text-5xl font-black text-white">{score.home}</span>
              <span className="text-2xl text-slate-500">-</span>
              <span className="text-5xl font-black text-white">{score.away}</span>
            </div>
            <div className="mt-4 text-xs font-bold text-slate-500 uppercase tracking-widest bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
              Full Time
            </div>
          </div>

          <div className="flex-1 text-center md:text-left">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">{away_team}</h2>
            <div className="text-sm text-slate-400">Away</div>
          </div>
        </div>
      </div>

      {/* MATCH SUMMARY */}
      {summary && (
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl border border-slate-700 p-6 mb-8 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="bg-primary/20 p-3 rounded-lg text-primary">
              <ActivityIcon />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Match Insights</h3>
              <p className="text-slate-300 leading-relaxed">{summary}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* STATISTICS COMPARISON */}
        <div className="bg-surface rounded-xl border border-slate-700 shadow-lg p-6">
          <h3 className="text-xl font-bold text-white mb-8 flex items-center gap-2">
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
        <div className="bg-surface rounded-xl border border-slate-700 shadow-lg p-6 flex flex-col max-h-[700px]">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Clock size={20} /> Match Events
          </h3>
          
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
            {events && events.length > 0 ? (
              <div className="relative border-l-2 border-slate-700 ml-4 pl-6 pb-4 space-y-8">
                {events.map((ev: any, idx: number) => {
                  const isHome = ev.team === home_team;
                  return (
                    <div key={idx} className="relative">
                      {/* Timeline Dot */}
                      <div className="absolute -left-[35px] w-8 h-8 bg-slate-800 border border-slate-600 rounded-full flex items-center justify-center text-sm shadow-md">
                        {getEventIcon(ev.type)}
                      </div>
                      
                      <div className={`flex flex-col bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 ${isHome ? 'border-l-blue-500 border-l-4' : 'border-l-red-500 border-l-4'}`}>
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-bold text-white">{ev.minute}'</span>
                          <span className="text-xs text-textSecondary uppercase font-bold">{ev.type}</span>
                        </div>
                        <div className="text-sm font-medium text-slate-200">{ev.player}</div>
                        <div className="text-xs text-slate-400 mt-1">{ev.team}</div>
                        {ev.type === 'Substitution' && (
                          <div className="text-xs text-slate-400 italic mt-1">{ev.description}</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 italic border-2 border-dashed border-slate-700 rounded-xl">
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
