import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Activity, BarChart2, GitCompare, Info, Trophy, List, User, Users, Play, LineChart, History, Shield } from 'lucide-react';

const MainLayout: React.FC = () => {
  const location = useLocation();

  const navLinks = [
    { name: 'Predict', path: '/predict', icon: <Activity size={18} /> },
    { name: 'League', path: '/league', icon: <Trophy size={18} /> },
    { name: 'Matches', path: '/matches', icon: <List size={18} /> },
    { name: 'Players', path: '/players', icon: <User size={18} /> },
    { name: 'Player Compare', path: '/player-compare', icon: <Users size={18} /> },
    { name: 'Team Analysis', path: '/analysis', icon: <BarChart2 size={18} /> },
    { name: 'Team Compare', path: '/compare', icon: <GitCompare size={18} /> },
    { name: 'About', path: '/about', icon: <Info size={18} /> },
  ];

  return (
    <div className="min-h-screen flex flex-col font-sans">
      <header className="bg-surface border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="bg-primary text-white p-1.5 rounded-lg">
              <Activity size={24} />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">FootballWise</span>
          </Link>
          <nav className="hidden lg:flex items-center gap-1 xl:gap-3">
            {navLinks.map((link) => (
              <Link 
                key={link.name} 
                to={link.path}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md transition-colors text-sm ${
                  location.pathname === link.path 
                    ? 'text-primary bg-slate-800/50 font-semibold' 
                    : 'text-textSecondary hover:text-white hover:bg-slate-800/30 font-medium'
                }`}
              >
                {link.icon}
                <span>{link.name}</span>
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="flex-grow bg-background">
        <Outlet />
      </main>

      <footer className="bg-surface border-t border-slate-700 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-textSecondary">
          <p>© {new Date().getFullYear()} FootballWise. All rights reserved.</p>
          <p className="text-sm mt-2">Built for football analytics using StatsBomb Data.</p>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
