import React from 'react';
import { Info, Cpu, Database, Award } from 'lucide-react';

const AboutPage: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6">
      <div className="bg-slate-900/90 backdrop-blur-md p-8 sm:p-10 rounded-2xl border border-slate-700/80 shadow-2xl shadow-slate-950/50">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 text-white p-3 rounded-xl shadow-lg shadow-blue-500/20">
            <Info size={28} />
          </div>
          <div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-200 to-white">
              About FootballWise
            </h2>
            <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider mt-1">Platform Architecture & Data</p>
          </div>
        </div>

        <p className="text-slate-300 mb-8 leading-relaxed text-base sm:text-lg">
          FootballWise is an advanced analytics platform engineered for football enthusiasts, tactics analysts, and tactical professionals. 
          By combining rich event data with cutting-edge machine learning models, FootballWise delivers deep insights into 
          team performances, tactical nuances, and probability-based match predictions.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-slate-800/60 p-6 rounded-xl border border-slate-700/60">
            <div className="flex items-center gap-2.5 text-indigo-400 font-bold text-lg mb-4">
              <Cpu size={22} />
              <span>Technology Stack</span>
            </div>
            <ul className="space-y-2.5 text-slate-300 text-sm sm:text-base">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                <span><strong>Frontend:</strong> React 19, TypeScript, Vite, Tailwind CSS</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                <span><strong>Backend:</strong> FastAPI, Python 3.12, LangGraph AI Engine</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                <span><strong>Machine Learning:</strong> XGBoost, SHAP, Scikit-learn</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span><strong>LLM Provider:</strong> Groq (llama-3.3-70b-versatile / gpt-oss-120b)</span>
              </li>
            </ul>
          </div>

          <div className="bg-slate-800/60 p-6 rounded-xl border border-slate-700/60">
            <div className="flex items-center gap-2.5 text-blue-400 font-bold text-lg mb-4">
              <Database size={22} />
              <span>Data Architecture</span>
            </div>
            <ul className="space-y-2.5 text-slate-300 text-sm sm:text-base">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                <span><strong>Data Source:</strong> StatsBomb Open Data & Match Events</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span><strong>Vector Store:</strong> ChromaDB Vector RAG Engine</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                <span><strong>Relevance Guard:</strong> Zero-token deterministic local domain gate</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="bg-slate-800/40 p-6 rounded-xl border border-slate-700/50">
          <div className="flex items-center gap-2.5 text-emerald-400 font-bold text-lg mb-3">
            <Award size={22} />
            <span>Platform Vision</span>
          </div>
          <p className="text-slate-300 leading-relaxed text-sm sm:text-base">
            FootballWise empowers fans and sports analysts with transparent statistical explanations, avoiding hallucinated numbers through verified RAG context and feature attribution.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;

