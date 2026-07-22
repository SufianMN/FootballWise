import React, { useState } from 'react';

const PredictionPage: React.FC = () => {
  const [prediction, setPrediction] = useState<{
    homeWin: number; draw: number; awayWin: number; score: string;
  } | null>(null);

  const handlePredict = () => {
    // Mocked API response
    setPrediction({
      homeWin: 61,
      draw: 22,
      awayWin: 17,
      score: '2-1'
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h2 className="text-3xl font-bold mb-8 text-white">Match Prediction</h2>
      
      <div className="bg-surface p-6 rounded-xl border border-slate-700 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-textSecondary mb-2">Home Team</label>
            <select className="w-full bg-background border border-slate-600 rounded-lg p-3 text-white">
              <option>Arsenal</option>
              <option>Manchester City</option>
            </select>
          </div>
          <div>
            <label className="block text-textSecondary mb-2">Away Team</label>
            <select className="w-full bg-background border border-slate-600 rounded-lg p-3 text-white">
              <option>Real Madrid</option>
              <option>Barcelona</option>
            </select>
          </div>
        </div>
        <button 
          onClick={handlePredict}
          className="w-full bg-primary hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition-colors"
        >
          Generate Prediction
        </button>
      </div>

      {prediction && (
        <div className="bg-surface p-6 rounded-xl border border-slate-700 animate-fade-in">
          <h3 className="text-xl font-bold mb-6 text-center">Prediction Results</h3>
          <div className="flex justify-between items-center mb-8">
            <div className="text-center w-1/3">
              <div className="text-3xl font-bold text-secondary">{prediction.homeWin}%</div>
              <div className="text-textSecondary">Home Win</div>
            </div>
            <div className="text-center w-1/3">
              <div className="text-3xl font-bold text-slate-400">{prediction.draw}%</div>
              <div className="text-textSecondary">Draw</div>
            </div>
            <div className="text-center w-1/3">
              <div className="text-3xl font-bold text-red-500">{prediction.awayWin}%</div>
              <div className="text-textSecondary">Away Win</div>
            </div>
          </div>
          <div className="text-center border-t border-slate-600 pt-6">
            <div className="text-textSecondary mb-2">Predicted Score</div>
            <div className="text-4xl font-bold text-white">{prediction.score}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionPage;
