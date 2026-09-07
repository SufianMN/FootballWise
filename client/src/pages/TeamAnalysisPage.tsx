import React, { useState, useEffect } from 'react';
import { getTeams, getTeamAnalytics } from '../api';
import SearchableTeamSelect from '../components/SearchableTeamSelect/SearchableTeamSelect';
import { BarChart2 } from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

const TeamAnalysisPage: React.FC = () => {
  const [teams, setTeams] = useState<{ id: string; name: string }[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await getTeams();
        setTeams(response.data.data);
        if (response.data.data.length > 0) {
          setSelectedTeam(response.data.data[0].id);
        }
      } catch (err) {
        console.error("Failed to load teams:", err);
      }
    };
    fetchTeams();
  }, []);

  useEffect(() => {
    if (!selectedTeam) return;
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const response = await getTeamAnalytics(selectedTeam);
        setAnalytics(response.data.data);
      } catch (err) {
        console.error("Failed to fetch team analytics:", err);
        setAnalytics(null);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [selectedTeam]);

  if (loading || !analytics) {
    return (
      <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6">
        <div className="flex justify-between items-center mb-8">
          <div className="h-10 w-64 bg-slate-900/80 rounded-xl animate-pulse"></div>
          <div className="w-64 h-12 bg-slate-900/80 rounded-xl animate-pulse"></div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {[1,2,3,4,5,6].map(i => <div key={i} className="h-32 bg-slate-900/80 rounded-2xl animate-pulse"></div>)}
        </div>
        <div className="h-96 bg-slate-900/80 rounded-2xl animate-pulse"></div>
      </div>
    );
  }

  const { summary, trends, home_away } = analytics;

  // Prepare Home vs Away Data
  const homeAwayData = [
    { name: 'Win Rate %', home: Math.round(home_away.home.win_rate * 100), away: Math.round(home_away.away.win_rate * 100) },
    { name: 'Goals (Avg)', home: Math.round((home_away.home.goals_scored / home_away.home.matches) * 100) / 100 || 0, away: Math.round((home_away.away.goals_scored / home_away.away.matches) * 100) / 100 || 0 },
    { name: 'xG (Avg)', home: home_away.home.avg_xg, away: home_away.away.avg_xg },
    { name: 'Possession %', home: home_away.home.avg_possession, away: home_away.away.avg_possession },
    { name: 'Shots (Avg)', home: home_away.home.avg_shots, away: home_away.away.avg_shots },
  ];

  const disciplineData = [
    { name: 'Yellow Cards', count: summary.avg_yellow_cards * summary.matches, fill: '#eab308' },
    { name: 'Red Cards', count: summary.avg_red_cards * summary.matches, fill: '#ef4444' },
  ];

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 animate-fade-in">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
            <BarChart2 size={28} />
          </div>
          <div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
              Team Analytics Dashboard
            </h2>
            <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">StatsBomb Event Metrics & Performance Trends</p>
          </div>
        </div>

        <div className="w-full md:w-auto min-w-[260px]">
          <SearchableTeamSelect 
            teams={teams}
            value={selectedTeam}
            onChange={(id) => setSelectedTeam(id)}
            placeholder="Search team..."
          />
        </div>
      </div>

      {/* SECTION 1: Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 flex flex-col justify-center items-center text-center">
          <div className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-semibold">Matches</div>
          <div className="text-3xl font-black text-white">{summary.matches}</div>
        </div>
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 flex flex-col justify-center items-center text-center">
          <div className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-semibold">Win Rate</div>
          <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">{Math.round(summary.win_rate * 100)}%</div>
        </div>
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 flex flex-col justify-center items-center text-center">
          <div className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-semibold">Goals (Diff)</div>
          <div className="text-3xl font-black text-emerald-400">{summary.goals_scored} <span className="text-base text-slate-400 font-medium">({summary.goal_difference > 0 ? '+' : ''}{summary.goal_difference})</span></div>
        </div>
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 flex flex-col justify-center items-center text-center">
          <div className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-semibold">Avg xG</div>
          <div className="text-3xl font-black text-indigo-300">{summary.avg_xg}</div>
        </div>
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 flex flex-col justify-center items-center text-center">
          <div className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-semibold">Clean Sheets</div>
          <div className="text-3xl font-black text-white">{summary.clean_sheets}</div>
        </div>
        <div className="bg-slate-900/90 backdrop-blur-md p-5 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 flex flex-col justify-center items-center text-center">
          <div className="text-slate-400 text-xs mb-1 uppercase tracking-wider font-semibold">Avg Poss</div>
          <div className="text-3xl font-black text-blue-400">{summary.avg_possession}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* SECTION 2: Rolling Form */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 h-96">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Rolling Form (Win Rate %)</h3>
          <ResponsiveContainer width="100%" height="90%">
            <LineChart data={trends.form} margin={{ top: 5, right: 20, bottom: 25, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="match_date" stroke="#94a3b8" tick={{fontSize: 12}} angle={-45} textAnchor="end" />
              <YAxis stroke="#94a3b8" domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} dot={false} activeDot={{ r: 6 }} name="Win Rate %" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* SECTION 3: Expected Goals Trend */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 h-96">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Expected Goals (xG) Trend</h3>
          <ResponsiveContainer width="100%" height="90%">
            <LineChart data={trends.xg} margin={{ top: 5, right: 20, bottom: 25, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="match_date" stroke="#94a3b8" tick={{fontSize: 12}} angle={-45} textAnchor="end" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
              <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} dot={false} activeDot={{ r: 6 }} name="xG" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* SECTION 4: Goals Scored Trend */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 h-96">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Goals Scored Trend</h3>
          <ResponsiveContainer width="100%" height="90%">
            <LineChart data={trends.goals} margin={{ top: 5, right: 20, bottom: 25, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="match_date" stroke="#94a3b8" tick={{fontSize: 12}} angle={-45} textAnchor="end" />
              <YAxis stroke="#94a3b8" allowDecimals={false} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
              <Line type="stepAfter" dataKey="value" stroke="#f59e0b" strokeWidth={3} dot={false} activeDot={{ r: 6 }} name="Goals" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* SECTION 5: Possession Trend */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 h-96">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Possession Trend (%)</h3>
          <ResponsiveContainer width="100%" height="90%">
            <LineChart data={trends.possession} margin={{ top: 5, right: 20, bottom: 25, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="match_date" stroke="#94a3b8" tick={{fontSize: 12}} angle={-45} textAnchor="end" />
              <YAxis stroke="#94a3b8" domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
              <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={3} dot={false} activeDot={{ r: 6 }} name="Possession %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* SECTION 7: Home vs Away Grouped Bar Chart */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 lg:col-span-2 h-96">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Home vs Away Performance</h3>
          <ResponsiveContainer width="100%" height="88%">
            <BarChart data={homeAwayData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip cursor={{fill: '#334155', opacity: 0.4}} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Bar dataKey="home" name="Home" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              <Bar dataKey="away" name="Away" fill="#f43f5e" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* SECTION 8: Discipline Bar Chart */}
        <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 h-96">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Discipline Cards</h3>
          <ResponsiveContainer width="100%" height="88%">
            <BarChart data={disciplineData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" allowDecimals={false} />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" width={110} tick={{fontSize: 12}} />
              <Tooltip cursor={{fill: '#334155', opacity: 0.4}} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '0.75rem' }} />
              <Bar dataKey="count" name="Cards">
                {
                  disciplineData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))
                }
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default TeamAnalysisPage;

