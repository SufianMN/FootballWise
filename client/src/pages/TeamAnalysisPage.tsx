import React from 'react';

const TeamAnalysisPage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-white">Team Analysis</h2>
        <select className="bg-surface border border-slate-600 rounded-lg p-2 text-white min-w-[200px]">
          <option>Arsenal</option>
          <option>Manchester City</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <div className="text-textSecondary mb-2">Goals</div>
          <div className="text-3xl font-bold text-white">45</div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <div className="text-textSecondary mb-2">Expected Goals (xG)</div>
          <div className="text-3xl font-bold text-secondary">42.5</div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <div className="text-textSecondary mb-2">Possession</div>
          <div className="text-3xl font-bold text-white">55.2%</div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <div className="text-textSecondary mb-2">Pass Accuracy</div>
          <div className="text-3xl font-bold text-white">88.4%</div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <div className="text-textSecondary mb-2">Defensive Rating</div>
          <div className="text-3xl font-bold text-primary">7.5/10</div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <div className="text-textSecondary mb-2">Shots</div>
          <div className="text-3xl font-bold text-white">210</div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700 lg:col-span-2">
          <div className="text-textSecondary mb-2">Recent Form</div>
          <div className="flex gap-2 mt-2">
            <span className="bg-secondary text-white w-8 h-8 flex items-center justify-center rounded font-bold">W</span>
            <span className="bg-slate-500 text-white w-8 h-8 flex items-center justify-center rounded font-bold">D</span>
            <span className="bg-secondary text-white w-8 h-8 flex items-center justify-center rounded font-bold">W</span>
            <span className="bg-secondary text-white w-8 h-8 flex items-center justify-center rounded font-bold">W</span>
            <span className="bg-red-500 text-white w-8 h-8 flex items-center justify-center rounded font-bold">L</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamAnalysisPage;
