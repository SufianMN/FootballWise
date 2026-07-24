import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPlayerDetails } from '../api';
import { ChevronLeft, User, Shield, Activity, Target, Activity as Sprint, AlertCircle } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

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
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="h-64 bg-surface rounded-xl animate-pulse mb-8"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[1,2,3,4,5,6,7,8].map(i => <div key={i} className="h-24 bg-surface rounded-xl animate-pulse"></div>)}
        </div>
        <div className="h-96 bg-surface rounded-xl animate-pulse"></div>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="max-w-6xl mx-auto py-20 px-4 text-center">
        <AlertCircle size={48} className="mx-auto text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Player Not Found</h2>
        <p className="text-textSecondary mb-6">We couldn't find the statistics for this player.</p>
        <button onClick={() => navigate('/players')} className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors">
          Back to Database
        </button>
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
    <div className="max-w-6xl mx-auto py-8 px-4 animate-fade-in">
      <button 
        onClick={() => navigate('/players')}
        className="flex items-center gap-2 text-textSecondary hover:text-white mb-6 transition-colors"
      >
        <ChevronLeft size={18} /> Back to Database
      </button>

      {/* HEADER */}
      <div className="bg-surface rounded-2xl border border-slate-700 shadow-2xl p-8 mb-8 relative overflow-hidden flex flex-col md:flex-row items-center gap-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl -ml-32 -mb-32"></div>
        
        <div className="w-32 h-32 rounded-full bg-slate-800 border-4 border-slate-700 flex items-center justify-center text-slate-400 z-10 shadow-lg">
          <User size={64} />
        </div>
        
        <div className="flex-1 text-center md:text-left z-10">
          <h2 className="text-4xl font-bold text-white mb-2">{player.name}</h2>
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 mt-4">
            <div className="px-4 py-2 bg-slate-800 rounded-lg border border-slate-600 shadow-sm flex items-center gap-2">
              <Shield size={16} className="text-slate-400" />
              <span className="text-slate-200 font-medium">{player.team}</span>
            </div>
            <div className="px-4 py-2 bg-slate-800 rounded-lg border border-slate-600 shadow-sm flex items-center gap-2">
              <Sprint size={16} className="text-slate-400" />
              <span className="text-slate-200 font-medium">{player.position}</span>
            </div>
          </div>
        </div>

        <div className="text-center md:text-right z-10 bg-slate-900/50 p-4 rounded-xl border border-slate-700">
          <div className="text-sm text-slate-400 uppercase tracking-wider mb-1">Matches Analyzed</div>
          <div className="text-4xl font-black text-primary">{player.matches}</div>
        </div>
      </div>

      {/* STAT CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
        <StatCard label="Goals" value={player.attacking.goals} icon={<Target size={16}/>} color="text-emerald-400" />
        <StatCard label="xG" value={player.attacking.xg.toFixed(2)} icon={<Activity size={16}/>} color="text-secondary" />
        <StatCard label="Assists" value={player.creativity.assists} color="text-blue-400" />
        <StatCard label="Pass Acc" value={`${Math.round(player.passing.pass_accuracy)}%`} color="text-white" />
        <StatCard label="Shots" value={player.attacking.shots} color="text-slate-300" />
        <StatCard label="Dribbles" value={player.dribbling.successful_dribbles} color="text-purple-400" />
        <StatCard label="Tackles" value={player.defending.tackles} color="text-orange-400" />
        <StatCard label="Y. Cards" value={player.discipline.yellow_cards} color="text-yellow-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* RADAR CHART */}
        <div className="bg-surface rounded-xl border border-slate-700 shadow-lg p-6 lg:col-span-1 h-[400px] flex flex-col">
          <h3 className="text-xl font-bold text-white mb-2">Player Percentiles</h3>
          <p className="text-xs text-textSecondary mb-4">Normalized per 90 metrics vs dataset</p>
          <div className="flex-1 -ml-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name={player.name} dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* DETAILED STATS */}
        <div className="bg-surface rounded-xl border border-slate-700 shadow-lg p-6 lg:col-span-2 flex flex-col gap-6">
          <h3 className="text-xl font-bold text-white mb-2">Detailed Profile</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-sm uppercase tracking-wider text-primary font-bold mb-4 border-b border-slate-700 pb-2">Attacking</h4>
              <DetailRow label="Goals per Match" value={player.attacking.goals_per_match.toFixed(2)} />
              <DetailRow label="xG per Match" value={player.attacking.xg_per_match.toFixed(2)} />
              <DetailRow label="Shots on Target" value={player.attacking.shots_on_target} />
              <DetailRow label="Shot Acc %" value={`${Math.round(player.attacking.shot_accuracy)}%`} />
              <DetailRow label="Goal Conversion" value={`${Math.round(player.advanced.shot_conversion)}%`} />
            </div>

            <div>
              <h4 className="text-sm uppercase tracking-wider text-secondary font-bold mb-4 border-b border-slate-700 pb-2">Possession</h4>
              <DetailRow label="Total Passes" value={player.passing.passes} />
              <DetailRow label="Completed Passes" value={player.passing.completed_passes} />
              <DetailRow label="Key Passes" value={player.creativity.key_passes} />
              <DetailRow label="Attempted Dribbles" value={player.dribbling.dribbles} />
              <DetailRow label="Dribble Success" value={`${Math.round(player.dribbling.dribble_success)}%`} />
            </div>

            <div>
              <h4 className="text-sm uppercase tracking-wider text-orange-400 font-bold mb-4 border-b border-slate-700 pb-2">Defending & Discip.</h4>
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
  <div className="bg-surface border border-slate-700 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-md hover:border-slate-500 transition-colors">
    <div className="text-xs text-textSecondary uppercase tracking-wider mb-2 font-medium flex items-center gap-1">
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
