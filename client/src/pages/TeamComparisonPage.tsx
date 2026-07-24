import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTeams, getTeamStats } from '../api';

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
        setTeams(response.data);
        if (response.data.length >= 2) {
          setTeamAId(response.data[0].id);
          setTeamBId(response.data[1].id);
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
        setTeamAStats(res.data);
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
        setTeamBStats(res.data);
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
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h2 className="text-3xl font-bold text-white mb-8">Team Comparison</h2>
      
      <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 bg-surface p-4 rounded-xl border border-slate-700 shadow-md">
        <select 
          value={teamAId}
          onChange={(e) => setTeamAId(e.target.value)}
          className="w-full md:w-auto bg-background border border-slate-600 rounded-lg p-3 text-white focus:border-primary outline-none"
        >
          {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        <div className="text-textSecondary font-bold bg-background px-4 py-2 rounded-full border border-slate-700 shadow-inner">
          VS
        </div>
        <select 
          value={teamBId}
          onChange={(e) => setTeamBId(e.target.value)}
          className="w-full md:w-auto bg-background border border-slate-600 rounded-lg p-3 text-white focus:border-primary outline-none"
        >
          {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>

      <div className="bg-surface p-6 rounded-xl border border-slate-700 h-[500px] shadow-lg animate-fade-in relative">
        <h3 className="text-xl font-bold text-white mb-6">Performance Metrics Comparison</h3>
        
        {(loadingA || loadingB) ? (
          <div className="absolute inset-0 flex items-center justify-center bg-surface/80 rounded-xl z-10">
            <div className="w-12 h-12 border-4 border-slate-600 border-t-primary rounded-full animate-spin"></div>
          </div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} tick={{fill: '#e2e8f0'}} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc', borderRadius: '0.5rem' }}
                itemStyle={{ color: '#f8fafc', fontWeight: 'bold' }}
                cursor={{fill: '#334155', opacity: 0.4}}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="teamA" name={teamAName} fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
              <Bar dataKey="teamB" name={teamBName} fill="#10b981" radius={[0, 4, 4, 0]} barSize={20} />
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
