import React, { useState, useEffect, useMemo } from 'react';
import { getPlayers, comparePlayers } from '../api';
import SearchablePlayerSelect from "../components/SearchablePlayerSelect/SearchablePlayerSelect";
import type { Player } from "../components/SearchablePlayerSelect/SearchablePlayerSelect";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Users } from 'lucide-react';

const PlayerComparePage: React.FC = () => {
  const [playersList, setPlayersList] = useState<Player[]>([]);
  const [player1Id, setPlayer1Id] = useState<string>('');
  const [player2Id, setPlayer2Id] = useState<string>('');

  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchPlayersList = async () => {
      try {
        const res = await getPlayers();
        setPlayersList(res.data.data);
      } catch (err) {
        console.error("Failed to load players:", err);
      }
    };
    fetchPlayersList();
  }, []);

  useEffect(() => {
    if (!player1Id || !player2Id) return;
    const fetchComparison = async () => {
      setLoading(true);
      try {
        const res = await comparePlayers(parseInt(player1Id), parseInt(player2Id));
        setComparison(res.data.data);
      } catch (err) {
        console.error("Failed to fetch comparison:", err);
        setComparison(null);
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, [player1Id, player2Id]);

  const p1 = comparison?.player1;
  const p2 = comparison?.player2;

  const radarData = useMemo(() => {
    if (!p1 || !p2) return [];
    return [
      { subject: 'Goals', P1: p1.radar.Goals, P2: p2.radar.Goals, fullMark: 100 },
      { subject: 'xG', P1: p1.radar.xG, P2: p2.radar.xG, fullMark: 100 },
      { subject: 'Assists', P1: p1.radar.Assists, P2: p2.radar.Assists, fullMark: 100 },
      { subject: 'Passing', P1: p1.radar.Passing, P2: p2.radar.Passing, fullMark: 100 },
      { subject: 'Dribbling', P1: p1.radar.Dribbling, P2: p2.radar.Dribbling, fullMark: 100 },
      { subject: 'Defending', P1: p1.radar.Defending, P2: p2.radar.Defending, fullMark: 100 },
      { subject: 'Progression', P1: p1.radar.Progression, P2: p2.radar.Progression, fullMark: 100 },
    ];
  }, [p1, p2]);

  const barData = useMemo(() => {
    if (!p1 || !p2) return [];
    return [
      { name: 'Goals/Match', P1: p1.attacking.goals_per_match, P2: p2.attacking.goals_per_match },
      { name: 'xG/Match', P1: p1.attacking.xg_per_match, P2: p2.attacking.xg_per_match },
      { name: 'Key Passes', P1: p1.creativity.key_passes, P2: p2.creativity.key_passes },
      { name: 'Dribbles', P1: p1.dribbling.successful_dribbles, P2: p2.dribbling.successful_dribbles },
      { name: 'Tackles', P1: p1.defending.tackles, P2: p2.defending.tackles },
    ];
  }, [p1, p2]);

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
          <Users size={28} />
        </div>
        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
            Player Head-to-Head Compare
          </h2>
          <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">Radar & Statistical Performance Breakdown</p>
        </div>
      </div>

      {/* SELECTORS */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 relative z-30">
        <div className="w-full md:w-5/12">
          <label className="block text-slate-300 mb-2 text-xs font-bold uppercase tracking-wider">Player 1</label>
          <SearchablePlayerSelect
            players={playersList}
            value={player1Id}
            onChange={(id) => setPlayer1Id(id)}
            placeholder="Search first player..."
          />
        </div>

        <div className="text-blue-400 font-black tracking-widest bg-slate-950 px-5 py-2.5 rounded-2xl border border-blue-500/40 shadow-lg text-sm md:mt-6">
          VS
        </div>

        <div className="w-full md:w-5/12">
          <label className="block text-slate-300 mb-2 text-xs font-bold uppercase tracking-wider">Player 2</label>
          <SearchablePlayerSelect
            players={playersList}
            value={player2Id}
            onChange={(id) => setPlayer2Id(id)}
            placeholder="Search second player..."
          />
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-64 bg-slate-900/90 rounded-2xl border border-slate-700/80">
          <div className="w-10 h-10 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
      )}

      {!loading && !comparison && (
        <div className="flex items-center justify-center h-64 bg-slate-900/40 rounded-2xl border border-dashed border-slate-800 text-slate-500 font-medium">
          Select two players to see their head-to-head comparison.
        </div>
      )}

      {!loading && p1 && p2 && (
        <div className="space-y-8 animate-fade-in">

          {/* HEADER COMPARISON */}
          <div className="grid grid-cols-3 bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 overflow-hidden text-center divide-x divide-slate-800">
            <div className="p-6 bg-blue-950/30">
              <h3 className="text-2xl font-black text-blue-400 mb-1">{p1.name}</h3>
              <div className="text-slate-400 text-sm font-medium">{p1.team} • {p1.position}</div>
            </div>
            <div className="p-6 flex flex-col justify-center bg-slate-950/60">
              <span className="text-slate-500 font-bold uppercase tracking-widest text-xs">Matches Played</span>
              <span className="text-white text-2xl font-black">{p1.matches} <span className="text-slate-600 mx-2">|</span> {p2.matches}</span>
            </div>
            <div className="p-6 bg-emerald-950/30">
              <h3 className="text-2xl font-black text-emerald-400 mb-1">{p2.name}</h3>
              <div className="text-slate-400 text-sm font-medium">{p2.team} • {p2.position}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* RADAR OVERLAY */}
            <div className="bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 p-6 h-[520px] flex flex-col">
              <h3 className="text-xl font-bold text-slate-100 mb-2 text-center">Style Overlay (Percentiles)</h3>
              <div className="flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name={p1.name} dataKey="P1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
                    <Radar name={p2.name} dataKey="P2" stroke="#10b981" fill="#10b981" fillOpacity={0.4} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* RAW STATS BAR CHART */}
            <div className="bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 p-6 h-[520px] flex flex-col">
              <h3 className="text-xl font-bold text-slate-100 mb-6 text-center">Key Output Comparison</h3>
              <div className="flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} tick={{ fill: '#e2e8f0' }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '0.75rem' }}
                      cursor={{ fill: '#334155', opacity: 0.4 }}
                    />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                    <Bar dataKey="P1" name={p1.name} fill="#3b82f6" radius={[0, 6, 6, 0]} barSize={22} />
                    <Bar dataKey="P2" name={p2.name} fill="#10b981" radius={[0, 6, 6, 0]} barSize={22} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
};

export default PlayerComparePage;
