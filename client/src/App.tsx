import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import PredictionPage from './pages/PredictionPage';
import TeamAnalysisPage from './pages/TeamAnalysisPage';
import TeamComparisonPage from './pages/TeamComparisonPage';
import LeaguePage from './pages/LeaguePage';
import MatchesPage from './pages/MatchesPage';
import MatchDetailsPage from './pages/MatchDetailsPage';
import AboutPage from './pages/AboutPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<LandingPage />} />
          <Route path="predict" element={<PredictionPage />} />
          <Route path="league" element={<LeaguePage />} />
          <Route path="matches" element={<MatchesPage />} />
          <Route path="match/:id" element={<MatchDetailsPage />} />
          <Route path="analysis" element={<TeamAnalysisPage />} />
          <Route path="compare" element={<TeamComparisonPage />} />
          <Route path="about" element={<AboutPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
