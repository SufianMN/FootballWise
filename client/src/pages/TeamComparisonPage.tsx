import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const mockData = [
  { name: 'Goals', teamA: 45, teamB: 40 },
  { name: 'xG', teamA: 42.5, teamB: 38.1 },
  { name: 'Possession', teamA: 55, teamB: 52 },
  { name: 'Pass Acc', teamA: 88, teamB: 85 },
  { name: 'Def Rating', teamA: 75, teamB: 70 },
];

const TeamComparisonPage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h2 className="text-3xl font-bold text-white mb-8">Team Comparison</h2>
      
      <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 bg-surface p-4 rounded-xl border border-slate-700">
        <select className="w-full md:w-auto bg-background border border-slate-600 rounded-lg p-2 text-white">
          <option>Arsenal</option>
          <option>Barcelona</option>
        </select>
        <div className="text-textSecondary font-bold">VS</div>
        <select className="w-full md:w-auto bg-background border border-slate-600 rounded-lg p-2 text-white">
          <option>Manchester City</option>
          <option>Real Madrid</option>
        </select>
      </div>

      <div className="bg-surface p-6 rounded-xl border border-slate-700 h-[500px]">
        <h3 className="text-xl font-bold text-white mb-6">Performance Metrics Comparison</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={mockData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
            <XAxis type="number" stroke="#94a3b8" />
            <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
              itemStyle={{ color: '#f8fafc' }}
            />
            <Legend />
            <Bar dataKey="teamA" name="Team A" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            <Bar dataKey="teamB" name="Team B" fill="#10b981" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TeamComparisonPage;
