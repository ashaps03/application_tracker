import axios from 'axios';
axios.defaults.withCredentials = true;

export default function ConnectGmail() {
    const handleGmailConnect = () => {
        window.open('http://localhost:8080/api/connect-gmail', '_blank');
      };

    return (
        <div>
        <button onClick={handleGmailConnect}>Connect Gmail</button>
      </div>
    );
  }
  