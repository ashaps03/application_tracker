import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css'; // ✅ correct path from within /src
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} /> 
      </Routes>
    </Router>
  );
}