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
    <div className="max-w-7xl mx-auto py-8 px-4 animate-fade-in">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Player Database</h2>
        <p className="text-textSecondary">Browse and search over {players.length.toLocaleString()} players from the StatsBomb dataset.</p>
      </div>

      {/* SEARCH BAR */}
      <div className="bg-surface p-6 rounded-xl border border-slate-700 shadow-lg mb-8">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search size={20} className="text-slate-400" />
          </div>
          <input
            type="text"
            placeholder="Search by player name, team, or position..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-800 border border-slate-600 rounded-lg pl-12 p-4 text-white outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-lg"
          />
        </div>
      </div>

      {/* PLAYERS TABLE */}
      <div className="bg-surface rounded-xl border border-slate-700 shadow-lg overflow-hidden mb-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-textSecondary text-xs uppercase tracking-wider">
                <th className="px-6 py-4">Player</th>
                <th className="px-6 py-4">Team</th>
                <th className="px-6 py-4 text-right">Position</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={`skeleton-${i}`}>
                    <td colSpan={3} className="px-6 py-4">
                      <div className="h-10 bg-slate-800 rounded animate-pulse"></div>
                    </td>
                  </tr>
                ))
              ) : paginatedPlayers.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-6 py-12 text-center text-textSecondary">
                    <User size={48} className="mx-auto text-slate-600 mb-4" />
                    <p className="text-lg">No players found matching your search.</p>
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
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-400 group-hover:bg-primary/20 group-hover:text-primary transition-colors">
                          <User size={20} />
                        </div>
                        <span className="text-white font-bold text-lg group-hover:text-primary transition-colors">
                          {player.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-300 font-medium">
                      {player.team}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="inline-block bg-slate-800 border border-slate-600 px-3 py-1 rounded-full text-sm text-slate-300 font-medium">
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
        <div className="flex justify-between items-center bg-surface border border-slate-700 rounded-xl p-4 shadow-lg">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            <ChevronLeft size={18} /> Previous
          </button>
          <div className="text-textSecondary font-medium">
            Page <span className="text-white font-bold mx-1">{page}</span> of <span className="text-white font-bold mx-1">{totalPages}</span>
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

export default PlayersPage;
