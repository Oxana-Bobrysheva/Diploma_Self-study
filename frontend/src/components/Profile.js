import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const Profile = () => {
  const [profile, setProfile] = useState({});
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({ name: '', phone: '', city: '' });
  const [error, setError] = useState('');
  // New: State for courses
  const [courses, setCourses] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const [coursesError, setCoursesError] = useState('');

  const fetchProfile = useCallback(async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    setError('No access token found. Please log in.');
    return;
  }
  try {
    const response = await api.get('/users/profiles/me/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    setProfile(response.data);
    setFormData(response.data);
    setError('');
  } catch (err) {
    if (err.response?.status === 401) {
      setError('Session expired. Please log in again.');
      // Optional: Clear tokens and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    } else {
      setError('Failed to fetch profile.');
    }
  }
}, []);

  // New: Fetch courses function
  const fetchCourses = useCallback(async () => {
    try {
      const response = await api.get('/courses/');  // Uses your api.js getCourses logic
      setCourses(response.data);
      setCoursesError('');
    } catch (err) {
      setCoursesError('Failed to load courses.');
    } finally {
      setCoursesLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
    fetchCourses();  // Fetch both profile and courses on mount
  }, [fetchProfile, fetchCourses]);

  const handleEdit = () => {
    setEditing(true);
  };

  const handleSave = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    setError('No access token found. Please log in.');
    return;
  }
  try {
    const response = await api.put('/users/profiles/me/', formData, {
      headers: { Authorization: `Bearer ${token}` },
    });
    setProfile(response.data);
    setEditing(false);
    setError('');
  } catch (err) {
    if (err.response?.status === 401) {
      setError('Session expired. Please log in again.');
    } else {
      setError('Failed to update profile. Check your inputs.');
    }
  }
};

  const handleCancel = () => {
    setFormData({
      name: profile.name || '',
      phone: profile.phone || '',
      city: profile.city || ''
    });
    setEditing(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // New: Placeholder for viewing course details (we'll implement navigation later)
  const handleViewCourse = (courseId) => {
    // For now, just log or alert; later: navigate('/courses/' + courseId);
    alert(`Viewing details for course ${courseId} - CourseDetail.js coming soon!`);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>My Profile</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {editing ? (
        <div>
          <label>Name: <input name="name" value={formData.name} onChange={handleChange} /></label><br />
          <label>Phone: <input name="phone" value={formData.phone} onChange={handleChange} /></label><br />
          <label>City: <input name="city" value={formData.city} onChange={handleChange} /></label><br />
          <button onClick={handleSave}>Save</button>
          <button onClick={handleCancel}>Cancel</button>
        </div>
      ) : (
        <div>
          <p><strong>Name:</strong> {profile.name}</p>
          <p><strong>Email:</strong> {profile.email}</p>
          <p><strong>Phone:</strong> {profile.phone}</p>
          <p><strong>City:</strong> {profile.city}</p>
          <p><strong>Role:</strong> {profile.role}</p>
          <button onClick={handleEdit}>Edit Profile</button>
          <button onClick={() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');  // Optional: Also clear refresh token
            window.location.href = '/';
          }}>Logout</button>
        </div>
      )}

      {/* New: Courses Section */}
      <h2>My Courses</h2>
      {coursesLoading ? (
        <p>Loading courses...</p>
      ) : coursesError ? (
        <p style={{ color: 'red' }}>{coursesError}</p>
      ) : courses.length === 0 ? (
        <p>No courses enrolled yet.</p>
      ) : (
        <ul>
          {courses.map((course) => (
            <li key={course.id} style={{ marginBottom: '10px' }}>
              <h3>{course.title}</h3>
              <p>{course.description}</p>
              <button onClick={() => handleViewCourse(course.id)}>View Details</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Profile;
