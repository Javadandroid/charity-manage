import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import KioskQueue from './pages/KioskQueue';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col font-sans bg-background">
        <header className="bg-white shadow-sm py-4 px-6 border-b border-gray-100 sticky top-0 z-50">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary">سیستم مدیریت رویداد خیریه</h1>
            <nav className="space-x-4 space-x-reverse">
              <a href="/dashboard" className="text-slate-600 hover:text-primary transition-colors">داشبورد</a>
              <a href="/queue" className="text-slate-600 hover:text-primary transition-colors">نوبت‌دهی کیوسک</a>
            </nav>
          </div>
        </header>

        <main className="flex-grow container mx-auto p-4 md:p-6 lg:p-8">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/queue" element={<KioskQueue />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
