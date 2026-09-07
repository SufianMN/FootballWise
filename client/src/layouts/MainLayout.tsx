import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Activity, BarChart2, GitCompare, Info, Trophy, List, User, Users, Sparkles, Menu, X } from 'lucide-react';

const MainLayout: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Predict', path: '/predict', icon: <Activity className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'AI Analyst', path: '/ai-analyst', icon: <Sparkles className="w-4 h-4 xl:w-5 xl:h-5" />, isSpecial: true },
    { name: 'League', path: '/league', icon: <Trophy className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'Matches', path: '/matches', icon: <List className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'Players', path: '/players', icon: <User className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'Player Compare', path: '/player-compare', icon: <Users className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'Team Analysis', path: '/analysis', icon: <BarChart2 className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'Team Compare', path: '/compare', icon: <GitCompare className="w-4 h-4 xl:w-5 xl:h-5" /> },
    { name: 'About', path: '/about', icon: <Info className="w-4 h-4 xl:w-5 xl:h-5" /> },
  ];

  return (
    <div className="min-h-screen flex flex-col font-sans">
      {/* Expanded Taller Header without scrollbars */}
      <header className="bg-slate-900/95 backdrop-blur-md border-b border-slate-700/80 sticky top-0 z-50 shadow-xl shadow-slate-950/30">
        <div className="w-full max-w-[1800px] mx-auto px-3 sm:px-5 xl:px-8 h-20 xl:h-24 flex items-center justify-between gap-2 xl:gap-6">
          
          {/* Logo & Brand */}
          <Link 
            to="/" 
            className="flex items-center gap-2.5 xl:gap-3 px-2 py-1.5 rounded-xl transition-all duration-200 hover:opacity-95 group shrink-0"
          >
            <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-2 xl:p-2.5 rounded-2xl shadow-lg shadow-blue-500/25 border border-blue-400/20 group-hover:scale-105 transition-transform duration-200">
              <Activity className="w-6 h-6 xl:w-7 xl:h-7" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl lg:text-2xl xl:text-3xl font-extrabold text-white tracking-tight leading-none">
                Football<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">Wise</span>
              </span>
              <span className="text-[10px] xl:text-xs text-blue-400/90 font-medium tracking-wider uppercase mt-0.5">Analytics AI</span>
            </div>
          </Link>

          {/* Desktop Navigation - All Elements Always Visible, No Scrollbar */}
          <nav className="hidden lg:flex items-center justify-end flex-1 gap-1 lg:gap-1.5 xl:gap-2.5 2xl:gap-4">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link 
                  key={link.name} 
                  to={link.path}
                  className={`flex items-center gap-1.5 xl:gap-2 px-2.5 py-2 xl:px-3.5 xl:py-2.5 2xl:px-4 2xl:py-3 rounded-xl text-xs lg:text-sm xl:text-base 2xl:text-lg transition-all duration-200 whitespace-nowrap ${
                    isActive 
                      ? 'bg-gradient-to-r from-blue-600/35 to-indigo-600/35 text-white font-bold border border-blue-500/60 shadow-lg shadow-blue-500/20 scale-[1.02]' 
                      : link.isSpecial
                        ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-200 border border-indigo-500/40 hover:text-white hover:bg-indigo-500/30 font-semibold shadow-sm'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/80 border border-transparent hover:border-slate-700/60 font-medium'
                  }`}
                >
                  <span className={`${isActive ? 'text-blue-400' : link.isSpecial ? 'text-purple-300' : 'text-slate-400'}`}>
                    {link.icon}
                  </span>
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 focus:outline-none"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X size={26} /> : <Menu size={26} />}
          </button>
        </div>

        {/* Mobile Navigation Dropdown */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-slate-900 border-b border-slate-700/80 px-4 py-4 space-y-2">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/30 text-white font-bold border border-blue-500/50'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {link.icon}
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </div>
        )}
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


