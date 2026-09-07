import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart2, GitCompare, Sparkles, ArrowRight, Zap } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="relative min-h-[85vh] flex flex-col items-center justify-center text-center px-4 py-12 overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-blue-600/20 via-indigo-600/15 to-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Pill Badge */}
      <div className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/40 rounded-full px-4 py-1.5 text-xs xl:text-sm font-semibold tracking-wide uppercase mb-6 shadow-md shadow-indigo-500/10">
        <Sparkles size={16} className="text-purple-400" />
        <span>Next-Gen Football Analytics Platform</span>
      </div>

      <h1 className="text-4xl sm:text-6xl xl:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white tracking-tight mb-6 max-w-4xl leading-tight">
        Match Predictions & AI Analytics Powered by Data
      </h1>

      <p className="text-base sm:text-xl text-slate-300 mb-10 max-w-2xl leading-relaxed">
        Leverage machine learning, StatsBomb Open Data, XGBoost models, and SHAP explainability for tactical insights and fixture forecasts.
      </p>

      <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
        <Link 
          to="/predict" 
          className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-lg py-3.5 px-8 rounded-xl shadow-lg shadow-blue-500/25 border border-blue-400/20 active:scale-95 transition-all duration-200"
        >
          <span>Start Predicting</span>
          <ArrowRight size={20} />
        </Link>
        <Link 
          to="/ai-analyst" 
          className="flex items-center gap-2 bg-slate-900/90 hover:bg-slate-800 text-slate-200 font-bold text-lg py-3.5 px-8 rounded-xl border border-slate-700/80 hover:border-slate-600 active:scale-95 transition-all duration-200 shadow-xl"
        >
          <Sparkles size={20} className="text-indigo-400" />
          <span>Ask AI Analyst</span>
        </Link>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl text-left">
        <div className="bg-slate-900/90 backdrop-blur-md p-8 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 hover:border-blue-500/50 hover:shadow-blue-500/10 transition-all duration-300 group">
          <div className="bg-blue-600/20 text-blue-400 p-3 rounded-xl w-fit mb-5 border border-blue-500/30 group-hover:scale-110 transition-transform">
            <Zap size={24} />
          </div>
          <h3 className="text-xl font-bold mb-3 text-white group-hover:text-blue-400 transition-colors">Match Forecasts</h3>
          <p className="text-slate-400 leading-relaxed">Predict match outcomes with win/draw/loss probabilities, scorelines, and SHAP feature importance using XGBoost.</p>
        </div>

        <div className="bg-slate-900/90 backdrop-blur-md p-8 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 hover:border-indigo-500/50 hover:shadow-indigo-500/10 transition-all duration-300 group">
          <div className="bg-indigo-600/20 text-indigo-400 p-3 rounded-xl w-fit mb-5 border border-indigo-500/30 group-hover:scale-110 transition-transform">
            <BarChart2 size={24} />
          </div>
          <h3 className="text-xl font-bold mb-3 text-white group-hover:text-indigo-400 transition-colors">Team Analytics</h3>
          <p className="text-slate-400 leading-relaxed">Deep dive into team performance metrics, expected goals (xG), possession, and shot creation timelines.</p>
        </div>

        <div className="bg-slate-900/90 backdrop-blur-md p-8 rounded-2xl border border-slate-700/80 shadow-xl shadow-slate-950/40 hover:border-purple-500/50 hover:shadow-purple-500/10 transition-all duration-300 group">
          <div className="bg-purple-600/20 text-purple-400 p-3 rounded-xl w-fit mb-5 border border-purple-500/30 group-hover:scale-110 transition-transform">
            <GitCompare size={24} />
          </div>
          <h3 className="text-xl font-bold mb-3 text-white group-hover:text-purple-400 transition-colors">Tactical Comparisons</h3>
          <p className="text-slate-400 leading-relaxed">Compare teams and players head-to-head with interactive statistical breakdowns and radar charts.</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;

