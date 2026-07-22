import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <div className="bg-surface p-8 rounded-xl border border-slate-700">
        <h2 className="text-3xl font-bold text-primary mb-6">About FootballWise</h2>
        <p className="text-textSecondary mb-6 leading-relaxed">
          FootballWise is an advanced analytics platform designed for football enthusiasts, analysts, and professionals. 
          By combining rich event data with cutting-edge machine learning models, FootballWise provides deep insights into 
          team performances, tactical nuances, and match predictions.
        </p>
        <h3 className="text-xl font-bold text-white mb-4">Technology Stack</h3>
        <ul className="list-disc list-inside text-textSecondary mb-6 space-y-2">
          <li><strong>Frontend:</strong> React, TypeScript, Vite, Tailwind CSS</li>
          <li><strong>Backend:</strong> FastAPI, Python 3.12</li>
          <li><strong>Machine Learning:</strong> XGBoost, Scikit-learn, Pandas (Coming Soon)</li>
          <li><strong>Data Source:</strong> StatsBomb Open Data</li>
        </ul>
        <h3 className="text-xl font-bold text-white mb-4">Future Milestones</h3>
        <p className="text-textSecondary leading-relaxed">
          In future updates, FootballWise will implement live data ingestion pipelines, robust feature engineering based on 
          xG and possession metrics, and a fully trained predictive model using XGBoost to forecast match outcomes.
        </p>
      </div>
    </div>
  );
};

export default AboutPage;
