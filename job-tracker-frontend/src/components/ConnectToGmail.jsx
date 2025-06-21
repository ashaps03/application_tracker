import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuth } from 'firebase/auth';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

export default function ConnectGmail() {
  const [loading, setLoading] = useState(false);
  const [emails, setEmails] = useState([]);
  const [error, setError] = useState('');
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    const user = auth.currentUser;
    if (!user) return;

    axios.get(`http://localhost:8080/api/gmail-status?uid=${user.uid}`)
      .then(res => {
        setConnected(res.data.connected);
      })
      .catch(err => {
        console.error('Failed to check Gmail status:', err);
      });
  }, []);

  const handleToggle = async (e) => {
    const checked = e.target.checked;
    setConnected(checked);

    const auth = getAuth();
    const user = auth.currentUser;
    if (!user) {
      setError('User not logged in.');
      return;
    }

    const uid = user.uid;

    if (checked) {
      setLoading(true);
      setError('');
      setEmails([]);
      try {
        const res = await axios.post('http://localhost:8080/api/connect-gmail', { uid });
        setEmails(res.data.applications || []);
      } catch (err) {
        console.error(err);
        setError('Failed to connect Gmail.');
        setConnected(false);
      } finally {
        setLoading(false);
      }
    } else {
      try {
        await axios.post('http://localhost:8080/api/disconnect-gmail', { uid });
        setEmails([]);
      } catch (err) {
        console.error('Failed to disconnect Gmail:', err);
        setError('Failed to disconnect Gmail.');
        setConnected(true); // fallback
      }
    }
  };

  return (
    <div>
      <FormControlLabel
        control={
          <Switch
            checked={connected}
            onChange={handleToggle}
            disabled={loading}
          />
        }
        label={loading ? 'Connecting...' : 'Connect Gmail'}
      />

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {emails.length > 0 && (
        <div>
          <h3>📥 Fetched Job Application Emails:</h3>
          <ul>
            {emails.map((email, index) => (
              <li key={index}>
                <strong>{email.subject}</strong> <br />
                From: {email.from} <br />
                Date: {email.date} <br />
                Snippet: {email.snippet}
                <hr />
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
