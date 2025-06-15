import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

axios.defaults.withCredentials = true;

export default function SignUp() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); // Stop page reload

    try {
      const res = await axios.post('http://localhost:8080/api/signup', {
        name,
        email,
        password
      });
      console.log('Signup success:', res.data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Signup error:', error.response?.data || error.message);
      alert('Signup failed: ' + (error.response?.data?.error || 'Unknown error'));
    }
  };

  return (
    <div className="column is-4 is-offset-4">
      <h3 className="title">Sign Up</h3>
      <div className="box">
        <form onSubmit={handleSubmit}>
          <div className="field">
            <div className="control">
              <input
                className="input is-large"
                type="email"
                name="email"
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
                className="input is-large"
                type="text"
                name="name"
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
                className="input is-large"
                type="password"
                name="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="button is-block is-info is-large is-fullwidth">
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
}
