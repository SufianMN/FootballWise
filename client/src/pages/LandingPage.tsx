import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
      <h1 className="text-5xl font-bold text-primary mb-6">Welcome to FootballWise</h1>
      <p className="text-xl text-textSecondary mb-8 max-w-2xl">
        AI-powered football analytics and match prediction platform leveraging StatsBomb Open Data and machine learning.
      </p>
      <div className="flex gap-4">
        <Link to="/predict" className="bg-primary hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition-colors">
          Start Predicting
        </Link>
        <Link to="/analysis" className="bg-surface hover:bg-slate-700 text-white font-bold py-3 px-6 rounded-lg transition-colors border border-slate-600">
          View Analytics
        </Link>
      </div>
      
      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl">
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-bold mb-3 text-secondary">Match Prediction</h3>
          <p className="text-textSecondary">Predict match outcomes with win/draw/loss probabilities and scorelines using ML.</p>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-bold mb-3 text-secondary">Team Analysis</h3>
          <p className="text-textSecondary">Deep dive into team performance metrics, xG, possession, and form.</p>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-bold mb-3 text-secondary">Tactical Insights</h3>
          <p className="text-textSecondary">Compare teams head-to-head with interactive visualizations.</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
