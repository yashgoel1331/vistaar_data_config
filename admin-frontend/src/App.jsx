import { Routes, Route } from 'react-router-dom';
import DashboardLayout from './components/layout/DashboardLayout';
import GlossaryPage from './pages/GlossaryPage';
import AmbiguityPage from './pages/AmbiguityPage';
import AliasesEnGuPage from './pages/AliasesEnGuPage';
import AliasesEnglishPage from './pages/AliasesEnglishPage';
import ForbiddenPage from './pages/ForbiddenPage';
import PreferredPage from './pages/PreferredPage';
import SchemesPage from './pages/SchemesPage';
import ConfigManagementPage from './pages/ConfigManagementPage';

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route index element={<GlossaryPage />} />
        <Route path="ambiguity" element={<AmbiguityPage />} />
        <Route path="aliases/en-gu" element={<AliasesEnGuPage />} />
        <Route path="aliases/english" element={<AliasesEnglishPage />} />
        <Route path="forbidden" element={<ForbiddenPage />} />
        <Route path="preferred" element={<PreferredPage />} />
        <Route path="schemes" element={<SchemesPage />} />
        <Route path="config" element={<ConfigManagementPage />} />
      </Route>
    </Routes>
  );
}
