import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EventWizard from './pages/EventWizard';
import Kiosk from './pages/Kiosk';
import Booths from './pages/Booths';
import Products from './pages/Products';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="events" element={<EventWizard />} />
          <Route path="booths" element={<Booths />} />
          <Route path="products" element={<Products />} />
        </Route>
        <Route path="/kiosk" element={<Kiosk />} />
      </Routes>
    </Router>
  );
}

export default App;
