import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../firebase';
import {
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider
} from 'firebase/auth';

export default function SignUp() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const provider = new GoogleAuthProvider();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Optional: Save name manually in DB if needed
      const userCred = await createUserWithEmailAndPassword(auth, email, password);
      const idToken = await userCred.user.getIdToken();

      await fetch('http://localhost:8080/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: idToken
        },
        body: JSON.stringify({ name, email })
      });

      navigate('/dashboard');
    } catch (error) {
      console.error('Signup error:', error.message);
      alert('Signup failed: ' + error.message);
    }
  };

  const handleGoogleSignup = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const idToken = await result.user.getIdToken();

      await fetch('http://localhost:8080/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: idToken
        },
        body: JSON.stringify({ name: result.user.displayName, email: result.user.email })
      });

      navigate('/dashboard');
    } catch (err) {
      alert('❌ Google signup failed: ' + err.message);
    }
  };

  const handleSignIn = () => {
    navigate('/Login');
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
        <h3 className="title has-text-centered">Sign Up</h3>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <div className="control">
              <input
                className="input is-medium"
                type="text"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          </div>

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
            Sign Up
          </button>

          <button
            type="button"
            onClick={handleGoogleSignup}
            className="button is-danger is-light is-medium is-fullwidth"
            style={{ marginTop: '10px' }}
          >
            Sign Up with Google
          </button>

          <button
            type="button"
            onClick={handleSignIn}
            className="button is-light is-medium is-fullwidth"
            style={{ marginTop: '10px' }}
          >
            Already have an account? Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
