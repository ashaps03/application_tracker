import '../SignOutComponentCss.css'
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
axios.defaults.withCredentials = true;

export default function SignOut() {
    const navigate = useNavigate();
    const handleSignOut = async (e) => {
  
      try {
        const res = await axios.get('http://localhost:8080/api/signout');
        console.log('LogOut success:', res.data);
        navigate('/Login');
      } catch (error) {
        console.error('Login error:', error.response?.data || error.message);
        alert('Login failed: ' + (error.response?.data?.error || 'Unknown error'));
      }
    };

    return (
        <div className="icon" onClick={handleSignOut}>
        <i className="fas fa-sign-out-alt"></i>
      </div>
    );
  }
  