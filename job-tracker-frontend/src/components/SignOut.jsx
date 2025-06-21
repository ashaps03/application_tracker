import '../SignOutComponentCss.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
axios.defaults.withCredentials = true;

export default function SignOut() {
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      localStorage.removeItem('token');
      await axios.get('http://localhost:8080/api/signout');
      console.log('✅ Logged out successfully');
      navigate('/Login');
    } catch (error) {
      console.error('❌ Logout error:', error.response?.data || error.message);
      alert('Logout failed: ' + (error.response?.data?.error || 'Unknown error'));
    }
  };

  return (
    <div className="sign-out-container" onClick={handleSignOut}>
      <div className="sign-out-icon">
        <i className="fas fa-sign-out-alt"></i>
      </div>
      <span className="sign-out-text">Sign out</span>
    </div>
  );
}
