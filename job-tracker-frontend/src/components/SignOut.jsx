import '../SignOutComponentCss.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
axios.defaults.withCredentials = true;

export default function SignOut() {
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      // 🔥 Clear local token
      localStorage.removeItem('token');

      // 🔥 Notify backend (optional but good)
      await axios.get('http://localhost:8080/api/signout');

      console.log('✅ Logged out successfully');
      navigate('/Login');
    } catch (error) {
      console.error('❌ Logout error:', error.response?.data || error.message);
      alert('Logout failed: ' + (error.response?.data?.error || 'Unknown error'));
    }
  };

  return (
    <div className="icon" onClick={handleSignOut} title="Sign Out" style={{ cursor: 'pointer' }}>
      <i className="fas fa-sign-out-alt"></i>
    </div>
  );
}
