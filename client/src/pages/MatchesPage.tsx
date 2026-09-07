import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchMatches } from '../api';
import CustomSelect from '../components/CustomSelect/CustomSelect';
import { Search, ChevronLeft, ChevronRight, List } from 'lucide-react';

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
    const timer = setTimeout(() => {
      fetchMatches();
    }, 500);
    return () => clearTimeout(timer);
  }, [team, competition, page, sort]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
          <List size={28} />
        </div>
        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
            Historical Match Explorer
          </h2>
          <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">Browse {total > 0 ? total : ''} StatsBomb Matches</p>
        </div>
      </div>

      {/* FILTERS */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
            <Search size={18} className="text-slate-400" />
          </div>
          <input 
            type="text" 
            placeholder="Search by team (e.g. Arsenal)" 
            value={team}
            onChange={(e) => { setTeam(e.target.value); setPage(1); }}
            className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl pl-10 p-3.5 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all font-medium"
          />
        </div>
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
            <Search size={18} className="text-slate-400" />
          </div>
          <input 
            type="text" 
            placeholder="Search by competition (e.g. La Liga)" 
            value={competition}
            onChange={(e) => { setCompetition(e.target.value); setPage(1); }}
            className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl pl-10 p-3.5 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all font-medium"
          />
        </div>
        <CustomSelect 
          options={[
            { value: 'desc', label: 'Newest First' },
            { value: 'asc', label: 'Oldest First' }
          ]}
          value={sort}
          onChange={(val) => { setSort(val); setPage(1); }}
          className="min-w-[170px]"
        />
      </div>

      {/* MATCHES TABLE */}
      <div className="bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 text-slate-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Competition</th>
                <th className="px-6 py-4 text-right">Home Team</th>
                <th className="px-6 py-4 text-center">Score</th>
                <th className="px-6 py-4">Away Team</th>
                <th className="px-6 py-4">Winner</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={`skeleton-${i}`}>
                    <td colSpan={6} className="px-6 py-4">
                      <div className="h-6 bg-slate-800/80 rounded-lg animate-pulse"></div>
                    </td>
                  </tr>
                ))
              ) : matches.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                    No matches found matching your filters.
                  </td>
                </tr>
              ) : (
                matches.map((match) => (
                  <tr 
                    key={match.match_id} 
                    onClick={() => navigate(`/match/${match.match_id}`)}
                    className="hover:bg-slate-800/50 transition-colors cursor-pointer group"
                  >
                    <td className="px-6 py-4 text-slate-300 whitespace-nowrap">{match.date}</td>
                    <td className="px-6 py-4 text-slate-400 text-sm whitespace-nowrap">
                      <div className="font-semibold text-slate-200">{match.competition}</div>
                      <div className="text-xs text-slate-400">{match.season}</div>
                    </td>
                    <td className="px-6 py-4 text-white font-bold text-right">{match.home_team}</td>
                    <td className="px-6 py-4">
                      <div className="bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-1.5 text-center font-black text-white group-hover:border-blue-500 transition-colors shadow-inner">
                        {match.score}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-white font-bold">{match.away_team}</td>
                    <td className="px-6 py-4 text-slate-300 font-medium">
                      {match.winner === 'Draw' ? <span className="text-slate-400">Draw</span> : <span className="text-emerald-400 font-semibold">{match.winner}</span>}
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
        <div className="flex justify-between items-center bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-2xl p-4 shadow-xl">
          <button 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-semibold transition-all"
          >
            <ChevronLeft size={18} /> Previous
          </button>
          <div className="text-slate-400 text-sm">
            Page <span className="text-white font-bold">{page}</span> of <span className="text-white font-bold">{totalPages}</span>
          </div>
          <button 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages || loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-semibold transition-all"
          >
            Next <ChevronRight size={18} />
          </button>
        </div>
      )}

    </div>
  );
};

export default MatchesPage;

