import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlayers } from '../api';
import { Search, ChevronLeft, ChevronRight, User } from 'lucide-react';
import type { Player } from "../components/SearchablePlayerSelect/SearchablePlayerSelect";

const PlayersPage: React.FC = () => {
  const navigate = useNavigate();
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        const res = await getPlayers();
        setPlayers(res.data.data);
      } catch (err) {
        console.error("Failed to load players:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPlayers();
  }, []);

  const filteredPlayers = useMemo(() => {
    if (!searchTerm.trim()) return players;
    const lower = searchTerm.toLowerCase().trim();
    return players.filter(p =>
      p.name.toLowerCase().includes(lower) ||
      p.team.toLowerCase().includes(lower) ||
      p.position.toLowerCase().includes(lower)
    );
  }, [players, searchTerm]);

  // Pagination logic
  const totalPages = Math.ceil(filteredPlayers.length / pageSize);

  // Reset page when search changes
  useEffect(() => {
    setPage(1);
  }, [searchTerm]);

  const paginatedPlayers = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredPlayers.slice(start, start + pageSize);
  }, [filteredPlayers, page]);

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20">
          <User size={28} />
        </div>
        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
            Player Database
          </h2>
          <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">Browse {players.length.toLocaleString()} StatsBomb Players</p>
        </div>
      </div>

      {/* SEARCH BAR */}
      <div className="bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 mb-8">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search size={20} className="text-slate-400" />
          </div>
          <input
            type="text"
            placeholder="Search by player name, team, or position..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl pl-12 p-4 text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all text-base sm:text-lg font-medium"
          />
        </div>
      </div>

      {/* PLAYERS TABLE */}
      <div className="bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/40 overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 text-slate-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-4">Player</th>
                <th className="px-6 py-4">Team</th>
                <th className="px-6 py-4 text-right">Position</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={`skeleton-${i}`}>
                    <td colSpan={3} className="px-6 py-4">
                      <div className="h-10 bg-slate-800/80 rounded-xl animate-pulse"></div>
                    </td>
                  </tr>
                ))
              ) : paginatedPlayers.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center text-slate-400">
                    <User size={48} className="mx-auto text-slate-600 mb-4" />
                    <p className="text-lg font-medium">No players found matching your search.</p>
                  </td>
                </tr>
              ) : (
                paginatedPlayers.map((player) => (
                  <tr
                    key={player.id}
                    onClick={() => navigate(`/player/${player.id}`)}
                    className="hover:bg-slate-800/50 transition-colors cursor-pointer group"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3.5">
                        <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 group-hover:bg-blue-600/30 group-hover:text-blue-400 group-hover:border-blue-500/50 transition-all shadow-inner">
                          <User size={20} />
                        </div>
                        <span className="text-white font-bold text-lg group-hover:text-blue-400 transition-colors">
                          {player.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-300 font-semibold text-base">
                      {player.team}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-block bg-slate-950 border border-slate-700/80 px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-300 tracking-wider">
                        {player.position}
                      </span>
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
          <div className="text-slate-400 text-sm font-medium">
            Page <span className="text-white font-bold mx-1">{page}</span> of <span className="text-white font-bold mx-1">{totalPages}</span>
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

export default PlayersPage;

