import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPlayerDetails } from '../api';
import { ChevronLeft, User, Shield, Activity, Target, Activity as Sprint, AlertCircle } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

const PlayerDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [player, setPlayer] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchPlayer = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const res = await getPlayerDetails(parseInt(id));
        setPlayer(res.data.data);
      } catch (err) {
        console.error("Failed to load player details:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPlayer();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-12 px-4 space-y-8">
        <div className="h-64 bg-slate-900/80 border border-slate-700/80 rounded-2xl animate-pulse"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4,5,6,7,8].map(i => <div key={i} className="h-24 bg-slate-900/80 border border-slate-700/80 rounded-2xl animate-pulse"></div>)}
        </div>
        <div className="h-96 bg-slate-900/80 border border-slate-700/80 rounded-2xl animate-pulse"></div>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="max-w-6xl mx-auto py-20 px-4 text-center">
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-12 max-w-lg mx-auto">
          <AlertCircle size={56} className="mx-auto text-red-400 mb-4" />
          <h2 className="text-3xl font-extrabold text-white mb-2">Player Not Found</h2>
          <p className="text-slate-400 mb-6">We couldn't find the statistics for this player.</p>
          <button 
            onClick={() => navigate('/players')} 
            className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20 transition-all"
          >
            Back to Database
          </button>
        </div>
      </div>
    );
  }

  const radarData = [
    { subject: 'Goals', A: player.radar.Goals, fullMark: 100 },
    { subject: 'xG', A: player.radar.xG, fullMark: 100 },
    { subject: 'Assists', A: player.radar.Assists, fullMark: 100 },
    { subject: 'Passing', A: player.radar.Passing, fullMark: 100 },
    { subject: 'Dribbling', A: player.radar.Dribbling, fullMark: 100 },
    { subject: 'Defending', A: player.radar.Defending, fullMark: 100 },
    { subject: 'Progression', A: player.radar.Progression, fullMark: 100 },
  ];

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 animate-fade-in relative">
      {/* Background radial glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/15 blur-3xl rounded-full pointer-events-none"></div>

      <button 
        onClick={() => navigate('/players')}
        className="flex items-center gap-2 px-4 py-2 bg-slate-900/80 backdrop-blur-md border border-slate-700/80 rounded-xl text-slate-300 hover:text-white hover:border-slate-600 mb-6 transition-all text-sm font-semibold shadow-md"
      >
        <ChevronLeft size={18} /> Back to Database
      </button>

      {/* HEADER */}
      <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-8 mb-8 relative overflow-hidden flex flex-col md:flex-row items-center gap-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-indigo-600/10 rounded-full blur-3xl -ml-32 -mb-32 pointer-events-none"></div>
        
        <div className="w-32 h-32 rounded-full bg-slate-950/80 border-4 border-indigo-500/40 flex items-center justify-center text-indigo-400 z-10 shadow-xl shadow-indigo-950/50">
          <User size={64} />
        </div>
        
        <div className="flex-1 text-center md:text-left z-10">
          <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white mb-2">
            {player.name}
          </h2>
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mt-4">
            <div className="px-4 py-1.5 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/40 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-2 shadow-sm">
              <Shield size={14} className="text-indigo-400" />
              <span>{player.team}</span>
            </div>
            <div className="px-4 py-1.5 bg-slate-950/60 border border-slate-700/80 rounded-full text-slate-300 text-xs font-semibold uppercase tracking-wider flex items-center gap-2 shadow-sm">
              <Sprint size={14} className="text-cyan-400" />
              <span>{player.position}</span>
            </div>
          </div>
        </div>

        <div className="text-center md:text-right z-10 bg-slate-950/80 px-6 py-4 rounded-2xl border border-slate-700 shadow-inner">
          <div className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Matches Analyzed</div>
          <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">{player.matches}</div>
        </div>
      </div>

      {/* STAT CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
        <StatCard label="Goals" value={player.attacking.goals} icon={<Target size={16}/>} color="text-emerald-400" />
        <StatCard label="xG" value={player.attacking.xg.toFixed(2)} icon={<Activity size={16}/>} color="text-cyan-400" />
        <StatCard label="Assists" value={player.creativity.assists} color="text-blue-400" />
        <StatCard label="Pass Acc" value={`${Math.round(player.passing.pass_accuracy)}%`} color="text-slate-100" />
        <StatCard label="Shots" value={player.attacking.shots} color="text-indigo-300" />
        <StatCard label="Dribbles" value={player.dribbling.successful_dribbles} color="text-purple-400" />
        <StatCard label="Tackles" value={player.defending.tackles} color="text-amber-400" />
        <StatCard label="Y. Cards" value={player.discipline.yellow_cards} color="text-yellow-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* RADAR CHART */}
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-6 lg:col-span-1 h-[400px] flex flex-col">
          <h3 className="text-xl font-bold text-white mb-1">Player Percentiles</h3>
          <p className="text-xs text-slate-400 mb-4">Normalized per 90 metrics vs dataset</p>
          <div className="flex-1 -ml-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name={player.name} dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* DETAILED STATS */}
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 shadow-2xl rounded-2xl p-6 lg:col-span-2 flex flex-col gap-6">
          <h3 className="text-xl font-bold text-white mb-2">Detailed Profile</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-xs uppercase tracking-wider text-blue-400 font-bold mb-4 border-b border-slate-700/80 pb-2">Attacking</h4>
              <DetailRow label="Goals per Match" value={player.attacking.goals_per_match.toFixed(2)} />
              <DetailRow label="xG per Match" value={player.attacking.xg_per_match.toFixed(2)} />
              <DetailRow label="Shots on Target" value={player.attacking.shots_on_target} />
              <DetailRow label="Shot Acc %" value={`${Math.round(player.attacking.shot_accuracy)}%`} />
              <DetailRow label="Goal Conversion" value={`${Math.round(player.advanced.shot_conversion)}%`} />
            </div>

            <div>
              <h4 className="text-xs uppercase tracking-wider text-indigo-400 font-bold mb-4 border-b border-slate-700/80 pb-2">Possession</h4>
              <DetailRow label="Total Passes" value={player.passing.passes} />
              <DetailRow label="Completed Passes" value={player.passing.completed_passes} />
              <DetailRow label="Key Passes" value={player.creativity.key_passes} />
              <DetailRow label="Attempted Dribbles" value={player.dribbling.dribbles} />
              <DetailRow label="Dribble Success" value={`${Math.round(player.dribbling.dribble_success)}%`} />
            </div>

            <div>
              <h4 className="text-xs uppercase tracking-wider text-amber-400 font-bold mb-4 border-b border-slate-700/80 pb-2">Defending & Discip.</h4>
              <DetailRow label="Interceptions" value={player.defending.interceptions} />
              <DetailRow label="Clearances" value={player.defending.clearances} />
              <DetailRow label="Fouls Committed" value={player.discipline.fouls} />
              <DetailRow label="Yellow Cards" value={player.discipline.yellow_cards} />
              <DetailRow label="Red Cards" value={player.discipline.red_cards} />
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

const StatCard = ({ label, value, color, icon }: { label: string, value: string | number, color: string, icon?: React.ReactNode }) => (
  <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-2xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover:border-slate-600 transition-all">
    <div className="text-xs text-slate-400 uppercase tracking-wider mb-1 font-bold flex items-center gap-1">
      {icon} {label}
    </div>
    <div className={`text-2xl font-black ${color}`}>{value}</div>
  </div>
);

const DetailRow = ({ label, value }: { label: string, value: string | number }) => (
  <div className="flex justify-between items-center mb-3">
    <span className="text-slate-400 text-sm">{label}</span>
    <span className="text-white font-bold">{value}</span>
  </div>
);

export default PlayerDetailsPage;
