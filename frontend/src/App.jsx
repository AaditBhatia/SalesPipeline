import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LeadsList from './pages/LeadsList';
import AddLead from './pages/AddLead';
import LeadDetail from './pages/LeadDetail';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LeadsList />} />
        <Route path="/add-lead" element={<AddLead />} />
        <Route path="/leads/:id" element={<LeadDetail />} />
      </Routes>
    </Router>
  );
}

export default App;