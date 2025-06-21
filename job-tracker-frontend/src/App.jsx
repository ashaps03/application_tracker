import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './index.css'; // ✅ correct path from within /src
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import SignUp from './pages/SignUp';
import Login from './pages/Login';
import PrimarySearchAppBar from'./components/Navbar';


export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/SignUp" element={<SignUp />} />
        <Route path="/Login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} /> 
        <Route path="/Navbar" element={<PrimarySearchAppBar />} /> 
      </Routes>
    </Router>
  );
}