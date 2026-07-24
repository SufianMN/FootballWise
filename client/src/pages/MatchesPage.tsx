import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchMatches } from '../api';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';

const MatchesPage: React.FC = () => {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<any[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Filters
  const [team, setTeam] = useState<string>('');
  const [competition, setCompetition] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [sort, setSort] = useState<string>('desc');

  const fetchMatches = async () => {
    setLoading(true);
    try {
      const res = await searchMatches({ team, competition, page, sort, page_size: 20 });
      setMatches(res.data.data.matches);
      setTotal(res.data.data.total);
    } catch (err) {
      console.error("Failed to load matches:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Debounce typing
    const timer = setTimeout(() => {
      fetchMatches();
    }, 500);
    return () => clearTimeout(timer);
  }, [team, competition, page, sort]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 animate-fade-in">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Historical Match Explorer</h2>
        <p className="text-textSecondary">Browse {total > 0 ? total : ''} historical football matches from the StatsBomb dataset.</p>
      </div>

      {/* FILTERS */}
      <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={18} className="text-slate-400" />
          </div>
          <input 
            type="text" 
            placeholder="Search by team (e.g. Arsenal)" 
            value={team}
            onChange={(e) => { setTeam(e.target.value); setPage(1); }}
            className="w-full bg-slate-800 border border-slate-600 rounded-lg pl-10 p-3 text-white outline-none focus:border-primary transition-colors"
          />
        </div>
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={18} className="text-slate-400" />
          </div>
          <input 
            type="text" 
            placeholder="Search by competition (e.g. La Liga)" 
            value={competition}
            onChange={(e) => { setCompetition(e.target.value); setPage(1); }}
            className="w-full bg-slate-800 border border-slate-600 rounded-lg pl-10 p-3 text-white outline-none focus:border-primary transition-colors"
          />
        </div>
        <select 
          value={sort} 
          onChange={(e) => { setSort(e.target.value); setPage(1); }}
          className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-white outline-none focus:border-primary min-w-[150px]"
        >
          <option value="desc">Newest First</option>
          <option value="asc">Oldest First</option>
        </select>
      </div>

      {/* MATCHES TABLE */}
      <div className="bg-surface rounded-xl border border-slate-700 shadow-lg overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-textSecondary text-xs uppercase tracking-wider">
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Competition</th>
                <th className="px-6 py-4 text-right">Home Team</th>
                <th className="px-6 py-4 text-center">Score</th>
                <th className="px-6 py-4">Away Team</th>
                <th className="px-6 py-4">Winner</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={`skeleton-${i}`}>
                    <td colSpan={6} className="px-6 py-4">
                      <div className="h-6 bg-slate-800 rounded animate-pulse"></div>
                    </td>
                  </tr>
                ))
              ) : matches.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-textSecondary">
                    No matches found matching your filters.
                  </td>
                </tr>
              ) : (
                matches.map((match) => (
                  <tr 
                    key={match.match_id} 
                    onClick={() => navigate(`/match/${match.match_id}`)}
                    className="hover:bg-slate-800/30 transition-colors cursor-pointer group"
                  >
                    <td className="px-6 py-4 text-slate-300 whitespace-nowrap">{match.date}</td>
                    <td className="px-6 py-4 text-slate-400 text-sm whitespace-nowrap">
                      <div>{match.competition}</div>
                      <div className="text-xs text-slate-500">{match.season}</div>
                    </td>
                    <td className="px-6 py-4 text-white font-bold text-right">{match.home_team}</td>
                    <td className="px-6 py-4">
                      <div className="bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-center font-bold text-white group-hover:border-primary transition-colors">
                        {match.score}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-white font-bold">{match.away_team}</td>
                    <td className="px-6 py-4 text-slate-300">
                      {match.winner === 'Draw' ? <span className="text-slate-400">Draw</span> : <span className="text-emerald-400">{match.winner}</span>}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* PAGINATION */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center bg-surface border border-slate-700 rounded-xl p-4 shadow-lg">
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            <ChevronLeft size={18} /> Previous
          </button>
          <div className="text-textSecondary">
            Page <span className="text-white font-bold">{page}</span> of <span className="text-white font-bold">{totalPages}</span>
          </div>
          <button 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages || loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            Next <ChevronRight size={18} />
          </button>
        </div>
      )}

    </div>
  );
};

export default MatchesPage;
