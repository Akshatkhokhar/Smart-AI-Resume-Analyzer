import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Analyzer from './pages/Analyzer';
import JobSearch from './pages/JobSearch';
import Feedback from './pages/Feedback';
import ResumeBuilder from './pages/ResumeBuilder'; // Added import for ResumeBuilder

// Placeholder components for routes we haven't built yet
const Placeholder = ({ title }) => (
  <div className="flex items-center justify-center min-h-screen text-3xl text-gray-500">
    {title} Coming Soon
  </div>
);

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white font-sans">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyzer" element={<Analyzer />} />
          <Route path="/builder" element={<ResumeBuilder />} /> {/* Added ResumeBuilder route */}
          <Route path="/jobs" element={<JobSearch />} />
          <Route path="/feedback" element={<Feedback />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
