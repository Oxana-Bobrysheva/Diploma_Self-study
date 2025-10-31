import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../services/api';
import { setTokens } from '../utils/auth';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser(formData);
      setTokens(response.data.access, response.data.refresh);
      navigate('/');
    } catch (err) {
      setError('Invalid email or password');
    };
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
          style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
          style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
        />
        <button type="submit" style={{ padding: '10px', width: '100%' }}>Login</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p style={{ marginTop: '20px' }}>
        Don't have an account? <Link to="/signup">Sign up</Link>
      </p>
    </div>
  );
};

export default Login;
