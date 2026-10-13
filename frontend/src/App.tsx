import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { DigitalTwinMap } from './pages/DigitalTwinMap';
import { AttackSimulation } from './pages/AttackSimulation';
import { RemediationPlanning } from './pages/RemediationPlanning';
import { AssetInventory } from './pages/AssetInventory';
import { VulnerabilityManagement } from './pages/VulnerabilityManagement';
import { AssessmentManagement } from './pages/AssessmentManagement';
import { CVEIntelligence } from './pages/CVEIntelligence';
import { ReportsPage } from './pages/ReportsPage';

export function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-soc-bg text-slate-100 flex flex-col font-sans">
        <Navbar />
        <div className="flex-1 flex overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/" element={<OverviewDashboard />} />
              <Route path="/topology" element={<DigitalTwinMap />} />
              <Route path="/simulation" element={<AttackSimulation />} />
              <Route path="/remediation" element={<RemediationPlanning />} />
              <Route path="/assets" element={<AssetInventory />} />
              <Route path="/vulnerabilities" element={<VulnerabilityManagement />} />
              <Route path="/assessments" element={<AssessmentManagement />} />
              <Route path="/cve-intel" element={<CVEIntelligence />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
