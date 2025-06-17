import React, { useState } from 'react';
import axios from 'axios';
import { getAuth } from 'firebase/auth';

export default function ConnectGmail() {
  const [loading, setLoading] = useState(false);
  const [emails, setEmails] = useState([]);
  const [error, setError] = useState('');

  const handleConnect = async () => {
    setLoading(true);
    setError('');
    setEmails([]);

    try {
      const auth = getAuth();
      const user = auth.currentUser;
      if (!user) {
        setError('User not logged in.');
        setLoading(false);
        return;
      }

      const uid = user.uid;

      const res = await axios.post('http://localhost:8080/api/connect-gmail', {
        uid,
      });

      setEmails(res.data.applications || []);
    } catch (err) {
      console.error(err);
      setError('Failed to connect Gmail.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleConnect} disabled={loading}>
        {loading ? 'Connecting...' : 'Connect Gmail to Fetch Applications'}
      </button>

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
