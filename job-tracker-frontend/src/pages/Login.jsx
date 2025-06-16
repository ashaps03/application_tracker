import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../firebase'; // adjust path if needed
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
} from 'firebase/auth';

export default function LoginCard() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const provider = new GoogleAuthProvider();

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    try {
      const userCred = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCred.user.getIdToken();
      localStorage.setItem('token', idToken);

      console.log("✅ Email login token:", idToken);

      await fetch('http://localhost:8080/api/authcheck', {
        headers: {
          Authorization: idToken,
        },
      });

      navigate('/dashboard');
    } catch (err) {
      alert('❌ Login failed: ' + err.message);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const idToken = await result.user.getIdToken();
      console.log("✅ Google login token:", idToken);

      localStorage.setItem('token', idToken);


      await fetch('http://localhost:8080/api/authcheck', {
        headers: {
          Authorization: idToken,
        },
      });

      navigate('/dashboard');
    } catch (err) {
      alert('❌ Google login failed: ' + err.message);
    }
  };

  const handleSignUpClick = () => {
    navigate('/signup');
  };

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: '#f5f5f5'
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '400px',
          padding: '2rem',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.1)'
        }}
      >
        <h3 className="title has-text-centered">Welcome Back</h3>
        <form onSubmit={handleEmailLogin}>
          <div className="field">
            <div className="control">
              <input
                className="input is-medium"
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="field">
            <div className="control">
              <input
                className="input is-medium"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="button is-info is-medium is-fullwidth">
            Sign In
          </button>

          <button
            type="button"
            onClick={handleGoogleLogin}
            className="button is-danger is-light is-medium is-fullwidth"
            style={{ marginTop: '10px' }}
          >
            Sign in with Google
          </button>

          <button
            type="button"
            onClick={handleSignUpClick}
            className="button is-light is-medium is-fullwidth"
            style={{ marginTop: '10px' }}
          >
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
}
