import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EventWizard from './pages/EventWizard';
import Kiosk from './pages/Kiosk';
import Booths from './pages/Booths';
import Products from './pages/Products';
import Invoices from './pages/Invoices';
import Login from './pages/Login';
import Users from './pages/Users';
import ProtectedRoute from './components/ProtectedRoute';
import ToastContainer from './components/ToastContainer';

function App() {
  return (
    <>
      <ToastContainer />
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* Protected Dashboard Routes */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="events" element={<EventWizard />} />
          <Route path="booths" element={<Booths />} />
          <Route path="products" element={<Products />} />
          <Route path="invoices" element={<Invoices />} />
          <Route path="users" element={<Users />} />
        </Route>

        {/* Public or Tokenless Kiosk access */}
        <Route path="/kiosk" element={<Kiosk />} />
      </Routes>
    </Router>
    </>
  );
}

export default App;
