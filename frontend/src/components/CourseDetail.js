import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';  // Adjust path if needed

const CourseDetail = () => {
  const { id } = useParams();  // Get course ID from URL
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourse = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No access token found. Please log in.');
        setLoading(false);
        return;
      }

      try {
        console.log('Fetching course with ID:', id);  // Debug log
        const response = await api.get(`/courses/${id}/`, {  // Matches your endpoint: /api/courses/{id}/ (api.js adds /api)
          headers: { Authorization: `Bearer ${token}` },
        });
        console.log('Course data:', response.data);  // Debug log
        setCourse(response.data);
        setError('');
      } catch (err) {
        console.error('API Error:', err);  // Debug log
        if (err.response?.status === 401) {
          setError('Session expired. Please log in again.');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          navigate('/login');  // Redirect to login
        } else if (err.response?.status === 404) {
          setError('Course not found.');
        } else {
          setError('Failed to load course details.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [id, navigate]);

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading course details...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={() => navigate('/profile')}>Back to Profile</button>
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{ padding: '20px' }}>
        <p>Course not found.</p>
        <button onClick={() => navigate('/profile')}>Back to Profile</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>{course.title}</h2>
      <p>{course.description}</p>
      {course.materials && course.materials.length > 0 && (
        <div>
          <h3>Materials:</h3>
          <ul>
            {course.materials.map((material) => (
              <li key={material.id}>{material.title}</li>
            ))}
          </ul>
        </div>
      )}
      <button onClick={() => navigate('/profile')}>Back to Profile</button>
    </div>
  );
};

export default CourseDetail;
