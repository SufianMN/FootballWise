import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTeams, getTeamStats } from '../api';
import SearchableTeamSelect from '../components/SearchableTeamSelect/SearchableTeamSelect';
import { GitCompare } from 'lucide-react';

const TeamComparisonPage: React.FC = () => {
  const [teams, setTeams] = useState<{ id: string; name: string }[]>([]);
  const [teamAId, setTeamAId] = useState<string>('');
  const [teamBId, setTeamBId] = useState<string>('');
  const [teamAStats, setTeamAStats] = useState<any>(null);
  const [teamBStats, setTeamBStats] = useState<any>(null);
  const [loadingA, setLoadingA] = useState<boolean>(false);
  const [loadingB, setLoadingB] = useState<boolean>(false);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await getTeams();
        setTeams(response.data.data);
        if (response.data.data.length >= 2) {
          setTeamAId(response.data.data[0].id);
          setTeamBId(response.data.data[1].id);
        }
      } catch (err) {
        console.error("Failed to load teams:", err);
      }
    };
    fetchTeams();
  }, []);

  useEffect(() => {
    if (!teamAId) return;
    const fetchA = async () => {
      setLoadingA(true);
      try {
        const res = await getTeamStats(teamAId);
        setTeamAStats(res.data.data);
      } catch (err) {
        setTeamAStats(null);
      } finally {
        setLoadingA(false);
      }
    };
    fetchA();
  }, [teamAId]);

  useEffect(() => {
    if (!teamBId) return;
    const fetchB = async () => {
      setLoadingB(true);
      try {
        const res = await getTeamStats(teamBId);
        setTeamBStats(res.data.data);
      } catch (err) {
        setTeamBStats(null);
      } finally {
        setLoadingB(false);
      }
    };
    fetchB();
  }, [teamBId]);

  const chartData = useMemo(() => {
    if (!teamAStats || !teamBStats) return [];
    return [
      { name: 'Goals (Avg)', teamA: teamAStats.goals, teamB: teamBStats.goals },
      { name: 'xG', teamA: teamAStats.xg, teamB: teamBStats.xg },
      { name: 'Possession %', teamA: teamAStats.possession, teamB: teamBStats.possession },
      { name: 'Pass Acc %', teamA: teamAStats.passing_accuracy, teamB: teamBStats.passing_accuracy },
      { name: 'Clean Sheets', teamA: teamAStats.clean_sheets, teamB: teamBStats.clean_sheets },
      { name: 'Shots (Avg)', teamA: teamAStats.shots, teamB: teamBStats.shots },
    ];
  }, [teamAStats, teamBStats]);

  const teamAName = teamAStats?.name || 'Team A';
  const teamBName = teamBStats?.name || 'Team B';

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
          <GitCompare size={28} />
        </div>
        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
            Team Head-to-Head Comparison
          </h2>
          <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">Side-by-Side Tactical Metrics</p>
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 relative z-30">
        <div className="w-full md:w-5/12">
          <SearchableTeamSelect 
            teams={teams}
            value={teamAId}
            onChange={(id) => setTeamAId(id)}
            placeholder="Search Team A..."
          />
        </div>
        <div className="text-blue-400 font-black bg-slate-950 px-5 py-2.5 rounded-2xl border border-blue-500/40 shadow-lg tracking-widest text-sm">
          VS
        </div>
        <div className="w-full md:w-5/12">
          <SearchableTeamSelect 
            teams={teams}
            value={teamBId}
            onChange={(id) => setTeamBId(id)}
            placeholder="Search Team B..."
          />
        </div>
      </div>

      <div className="bg-slate-900/90 backdrop-blur-md p-6 sm:p-8 rounded-2xl border border-slate-700/80 h-[520px] shadow-2xl shadow-slate-950/40 animate-fade-in relative z-10">
        <h3 className="text-xl font-bold text-slate-100 mb-6">Performance Metrics Breakdown</h3>
        
        {(loadingA || loadingB) ? (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm rounded-2xl z-10">
            <div className="w-12 h-12 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="88%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} tick={{fill: '#e2e8f0'}} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '0.75rem' }}
                itemStyle={{ color: '#f8fafc', fontWeight: 'bold' }}
                cursor={{fill: '#334155', opacity: 0.4}}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="teamA" name={teamAName} fill="#3b82f6" radius={[0, 6, 6, 0]} barSize={22} />
              <Bar dataKey="teamB" name={teamBName} fill="#10b981" radius={[0, 6, 6, 0]} barSize={22} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center text-slate-500">
            Insufficient data for comparison.
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamComparisonPage;

