import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../services/api';

const Signup = () => {
  const [formData, setFormData] = useState({ email: '', password: '', phone: '', city: '', role: 'student' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await registerUser(formData);
      navigate('/login');
    } catch (err) {
      setError('Registration failed');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h2>Signup</h2>
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
        <input
          type="text"
          name="phone"
          placeholder="Phone (optional)"
          value={formData.phone}
          onChange={handleChange}
          style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
        />
        <input
          type="text"
          name="city"
          placeholder="City (optional)"
          value={formData.city}
          onChange={handleChange}
          style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
        />
        <select
          name="role"
          value={formData.role}
          onChange={handleChange}
          style={{ display: 'block', margin: '10px 0', padding: '8px', width: '100%' }}
        >
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
          <option value="admin">Admin</option>
        </select>
        <button type="submit" style={{ padding: '10px', width: '100%' }}>Sign Up</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p style={{ marginTop: '20px' }}>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
};

export default Signup;
