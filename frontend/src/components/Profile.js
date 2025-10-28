import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Profile = () => {
  const [profile, setProfile] = useState({});
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({ name: '', phone: '', city: '' });
  const [error, setError] = useState('');
  // State for courses (role-based)
  const [courses, setCourses] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const [coursesError, setCoursesError] = useState('');
  // New state for course creation form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [courseData, setCourseData] = useState({ title: '', description: '' });
  const [createError, setCreateError] = useState('');

  const navigate = useNavigate();

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
      const response = await api.get('/courses/my/');  // Uses your api.js getCourses logic
      setCourses(response.data.courses || []);
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

  // New: Handle course creation
  const handleCreateCourse = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) {
      setCreateError('No access token found. Please log in.');
      return;
    }
    try {
      const response = await api.post('/courses/', courseData, {  // Adjust endpoint if needed (e.g., '/api/courses/')
        headers: { Authorization: `Bearer ${token}` },
      });
      // Use response if needed (e.g., for success message) - this fixes the warning
      if (response.status === 201) {  // Assuming 201 for created
        alert('Course created successfully!');
      }
      setShowCreateForm(false);
      setCourseData({ title: '', description: '' });
      setCreateError('');
      fetchCourses();  // Refresh the courses list to show the new one
    } catch (err) {
      setCreateError('Failed to create course. Try again.');
      console.error(err);
    }
  };

  // New: Placeholder for viewing course details (we'll implement navigation later)
  const handleViewCourse = (courseId) => {
   navigate(`/courses/${courseId}`);
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
      {/* Conditionally show button for teachers/admins */}
      {(profile.role === 'teacher' || profile.role === 'admin') && (
        <button onClick={() => setShowCreateForm(true)} style={{ marginBottom: '10px' }}>
          Create New Course
        </button>
      )}
      {/* Show form if toggled */}
      {showCreateForm && (
        <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '20px' }}>
          <h3>Create New Course</h3>
          {createError && <p style={{ color: 'red' }}>{createError}</p>}
          <form onSubmit={handleCreateCourse}>
            <label>
              Title:
              <input
                type="text"
                name="title"
                value={courseData.title}
                onChange={(e) => setCourseData({ ...courseData, title: e.target.value })}
                required
              />
            </label>
            <br />
            <label>
              Description:
              <textarea
                name="description"
                value={courseData.description}
                onChange={(e) => setCourseData({ ...courseData, description: e.target.value })}
                required
              />
            </label>
            <br />
            <button type="submit">Create Course</button>
            <button type="button" onClick={() => { setShowCreateForm(false); setCourseData({ title: '', description: '' }); setCreateError(''); }}>
              Cancel
            </button>
          </form>
        </div>
      )}
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
