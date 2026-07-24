import React, { useState, useEffect } from 'react';
import { getCompetitions, getLeagueAnalytics } from '../api';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

const LeaguePage: React.FC = () => {
  const [competitions, setCompetitions] = useState<{ id: string; name: string }[]>([]);
  const [selectedComp, setSelectedComp] = useState<string>('');
  const [leagueData, setLeagueData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' } | null>(null);

  useEffect(() => {
    const fetchComps = async () => {
      try {
        const response = await getCompetitions();
        setCompetitions(response.data);
        if (response.data.length > 0) {
          setSelectedComp(response.data[0].id);
        }
      } catch (err) {
        console.error("Failed to load competitions:", err);
      }
    };
    fetchComps();
  }, []);

  useEffect(() => {
    if (!selectedComp) return;
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const response = await getLeagueAnalytics(selectedComp);
        setLeagueData(response.data);
      } catch (err) {
        console.error("Failed to fetch league analytics:", err);
        setLeagueData(null);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [selectedComp]);

  if (loading || !leagueData) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-white">League Intelligence</h2>
          <div className="w-64 h-12 bg-surface rounded-lg animate-pulse"></div>
        </div>
        <div className="h-96 bg-surface rounded-xl animate-pulse mb-8"></div>
        <div className="h-64 bg-surface rounded-xl animate-pulse"></div>
      </div>
    );
  }

  const { table, rankings, leaders, competition, season } = leagueData;

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'desc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });
  };

  const sortedTable = [...table].sort((a, b) => {
    if (!sortConfig) return 0;
    const { key, direction } = sortConfig;
    if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
    if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
    return 0;
  });

  // Prepare scatter data
  const scatterData = table.map((t: any) => ({
    name: t.team_name,
    x: t.avg_xg,
    y: t.avg_xga,
    fill: '#3b82f6'
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface border border-slate-600 p-3 rounded shadow-lg text-white">
          <p className="font-bold">{payload[0].payload.name}</p>
          <p className="text-emerald-400">Avg xG: {payload[0].payload.x}</p>
          <p className="text-red-400">Avg xGA: {payload[0].payload.y}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 animate-fade-in">
      {/* HEADER & SELECTOR */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white">League Intelligence</h2>
          <p className="text-textSecondary">{competition} &bull; {season}</p>
        </div>
        <select 
          value={selectedComp}
          onChange={(e) => setSelectedComp(e.target.value)}
          className="bg-surface border border-slate-600 rounded-lg p-3 text-white min-w-[300px] outline-none focus:border-primary shadow-lg"
        >
          {competitions.map(comp => (
            <option key={comp.id} value={comp.id}>{comp.name}</option>
          ))}
        </select>
      </div>

      {/* LEADERS CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-surface p-4 rounded-xl border border-emerald-900/50 shadow-md">
          <div className="text-emerald-400 text-sm mb-1 uppercase tracking-wider font-bold">🏆 Best Attack</div>
          <div className="text-xl font-bold text-white truncate">{leaders.best_attack_team}</div>
          <div className="text-sm text-textSecondary">{leaders.best_attack_val} Goals</div>
        </div>
        <div className="bg-surface p-4 rounded-xl border border-red-900/50 shadow-md">
          <div className="text-red-400 text-sm mb-1 uppercase tracking-wider font-bold">🛡 Best Defense</div>
          <div className="text-xl font-bold text-white truncate">{leaders.best_defense_team}</div>
          <div className="text-sm text-textSecondary">{leaders.best_defense_val} Conceded</div>
        </div>
        <div className="bg-surface p-4 rounded-xl border border-blue-900/50 shadow-md">
          <div className="text-blue-400 text-sm mb-1 uppercase tracking-wider font-bold">⚽ Highest xG</div>
          <div className="text-xl font-bold text-white truncate">{leaders.highest_xg_team}</div>
          <div className="text-sm text-textSecondary">{leaders.highest_xg_val} per game</div>
        </div>
        <div className="bg-surface p-4 rounded-xl border border-purple-900/50 shadow-md">
          <div className="text-purple-400 text-sm mb-1 uppercase tracking-wider font-bold">🔥 Best Form</div>
          <div className="text-xl font-bold text-white truncate">{leaders.best_form_team}</div>
          <div className="text-sm text-textSecondary">{leaders.best_form_val}% Win Rate</div>
        </div>
        <div className="bg-surface p-4 rounded-xl border border-yellow-900/50 shadow-md">
          <div className="text-yellow-400 text-sm mb-1 uppercase tracking-wider font-bold">🎯 Best Passing</div>
          <div className="text-xl font-bold text-white truncate">{leaders.best_pass_team}</div>
          <div className="text-sm text-textSecondary">{leaders.best_pass_val}% Accuracy</div>
        </div>
      </div>

      {/* STANDINGS TABLE */}
      <div className="bg-surface rounded-xl border border-slate-700 shadow-lg overflow-hidden mb-12">
        <div className="px-6 py-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
          <h3 className="text-lg font-bold text-white">League Standings</h3>
          <span className="text-xs text-textSecondary">Click columns to sort</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-textSecondary text-xs uppercase tracking-wider">
                <th className="px-6 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('position')}>Pos</th>
                <th className="px-6 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('team_name')}>Club</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('matches')}>MP</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('wins')}>W</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('draws')}>D</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('losses')}>L</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('goals_for')}>GF</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('goals_against')}>GA</th>
                <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('goal_difference')}>GD</th>
                <th className="px-6 py-3 font-bold cursor-pointer hover:text-white text-primary" onClick={() => handleSort('points')}>Pts</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {sortedTable.map((row) => (
                <tr key={row.team_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-3 text-white font-medium">{row.position}</td>
                  <td className="px-6 py-3 text-white font-bold">{row.team_name}</td>
                  <td className="px-4 py-3 text-slate-300">{row.matches}</td>
                  <td className="px-4 py-3 text-slate-300">{row.wins}</td>
                  <td className="px-4 py-3 text-slate-300">{row.draws}</td>
                  <td className="px-4 py-3 text-slate-300">{row.losses}</td>
                  <td className="px-4 py-3 text-slate-300">{row.goals_for}</td>
                  <td className="px-4 py-3 text-slate-300">{row.goals_against}</td>
                  <td className="px-4 py-3 text-slate-300">{row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}</td>
                  <td className="px-6 py-3 text-white font-bold">{row.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* ATTACK VS DEFENSE SCATTER */}
        <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg h-[450px]">
          <h3 className="text-lg font-bold text-white mb-2">Playstyle: Attack vs Defense</h3>
          <p className="text-sm text-textSecondary mb-6">Average xG vs Average xGA per match</p>
          <ResponsiveContainer width="100%" height="80%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" dataKey="x" name="Average xG" stroke="#94a3b8" label={{ value: 'Average xG (Attack)', position: 'insideBottom', offset: -10, fill: '#94a3b8' }} />
              <YAxis type="number" dataKey="y" name="Average xGA" stroke="#94a3b8" reversed label={{ value: 'Average xGA (Defense)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
              <Tooltip content={<CustomTooltip />} cursor={{strokeDasharray: '3 3'}} />
              <Scatter name="Teams" data={scatterData} fill="#8b5cf6">
                {
                  scatterData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))
                }
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* ADVANCED STATS TABLE */}
        <div className="bg-surface rounded-xl border border-slate-700 shadow-lg overflow-hidden h-[450px] flex flex-col">
          <div className="px-6 py-4 border-b border-slate-700 bg-slate-800/50">
            <h3 className="text-lg font-bold text-white">Advanced Team Metrics</h3>
          </div>
          <div className="overflow-y-auto flex-1 p-0">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 bg-slate-900 shadow">
                <tr className="text-textSecondary text-xs uppercase tracking-wider">
                  <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('team_name')}>Club</th>
                  <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('avg_possession')}>Poss %</th>
                  <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('avg_pass_accuracy')}>Pass Acc</th>
                  <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('avg_shots')}>Shots</th>
                  <th className="px-4 py-3 cursor-pointer hover:text-white" onClick={() => handleSort('clean_sheet_pct')}>CS %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {sortedTable.map((row) => (
                  <tr key={`adv-${row.team_id}`} className="hover:bg-slate-800/30">
                    <td className="px-4 py-3 text-white font-medium truncate max-w-[120px]">{row.team_name}</td>
                    <td className="px-4 py-3 text-slate-300">{row.avg_possession}%</td>
                    <td className="px-4 py-3 text-slate-300">{row.avg_pass_accuracy}%</td>
                    <td className="px-4 py-3 text-slate-300">{row.avg_shots}</td>
                    <td className="px-4 py-3 text-slate-300">{row.clean_sheet_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* RANKINGS BAR CHARTS */}
      <h3 className="text-2xl font-bold text-white mb-6">Top 5 Rankings</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        
        <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg h-72">
          <h4 className="text-md font-bold text-emerald-400 mb-4">Highest xG</h4>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={rankings.top_xg} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis dataKey="team_name" type="category" stroke="#94a3b8" width={100} tick={{fontSize: 12}} />
              <Tooltip cursor={{fill: '#334155', opacity: 0.4}} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
              <Bar dataKey="avg_xg" fill="#10b981" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg h-72">
          <h4 className="text-md font-bold text-blue-400 mb-4">Highest Possession %</h4>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={rankings.top_possession} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis dataKey="team_name" type="category" stroke="#94a3b8" width={100} tick={{fontSize: 12}} />
              <Tooltip cursor={{fill: '#334155', opacity: 0.4}} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
              <Bar dataKey="avg_possession" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg h-72">
          <h4 className="text-md font-bold text-purple-400 mb-4">Pass Accuracy %</h4>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={rankings.top_pass_accuracy} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis dataKey="team_name" type="category" stroke="#94a3b8" width={100} tick={{fontSize: 12}} />
              <Tooltip cursor={{fill: '#334155', opacity: 0.4}} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
              <Bar dataKey="avg_pass_accuracy" fill="#a855f7" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>

      </div>

    </div>
  );
};

export default LeaguePage;
