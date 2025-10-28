import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const truncateDescription = (text, maxWords = 20) => {
    if (!text) return '';
    const words = text.split(' ');
    if (words.length <= maxWords) {
      return text;
    }
    return words.slice(0, maxWords).join(' ') + '...';
  };

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError(null);

      // Create a FRESH axios instance JUST for this public call - no auth pollution
      const publicAxios = axios.create({
        baseURL: 'http://localhost:8000/api/',
        timeout: 5000,
      });

      // Explicitly override to ensure NO Authorization header
      const config = {
        headers: {
          'Content-Type': 'application/json',
          // NO 'Authorization' here - forces anonymous
        },
        withCredentials: false,  // No cookies/sessions
      };

      console.log('Making PUBLIC request with config:', config);  // Debug: Check no auth

      const response = await publicAxios.get('courses/', config);

      console.log('SUCCESS - Full Public API Response:', response.data);
      console.log('Request Headers Sent:', response.config.headers);  // Verify no Authorization

      setCourses(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('FULL ERROR DETAILS:', err);  // Log everything for debugging
      console.error('Response Status:', err.response?.status);
      console.error('Response Data:', err.response?.data);
      console.error('Request Config/Headers:', err.config?.headers);  // This will show if token was sent!

      if (err.response?.status === 401 || err.response?.status === 403) {
        setError(`Auth error (401/403) - Token interference detected! Clear localStorage and retry.`);
      } else if (err.code === 'ECONNABORTED') {
        setError('Request timed out - Check if backend is running.');
      } else {
        setError(`Failed to load courses: ${err.message}`);
      }
      setCourses([]);  // Empty on error to avoid map crashes
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Clear any potential stale token before fetch (temporary debug step)
    if (localStorage.getItem('token')) {
      console.log('Clearing stale token for public test...');
      localStorage.removeItem('token');
    }
    fetchCourses();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', fontSize: '18px' }}>
        Loading courses... ⏳
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <div style={{ maxWidth: '1200px', width: '100%' }}>
        <h1 style={{ color: 'green', textAlign: 'center', marginBottom: '10px' }}>
          Ознакомьтесь с нашими курсами
        </h1>
        <p style={{ color: 'white', textAlign: 'center', marginBottom: '30px' }}>
          Get acquainted with our courses below.
        </p>

        {error && (
          <div style={{
            color: 'yellow',
            background: 'rgba(0,0,0,0.2)',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            ⚠️ {error}
            <br />
            <small>Check console for full details. Clear browser cache/localStorage if needed.</small>
          </div>
        )}

        {courses.length === 0 && !loading ? (
          <p style={{ textAlign: 'center', color: 'white' }}>
            No courses available yet. {error ? '' : '(Backend might be empty—add some data!)'}
          </p>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px',
            marginBottom: '30px'
          }}>
            {courses.map((course) => (
              <div key={course.id} style={{
                background: 'white',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                textAlign: 'center'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#333' }}>{course.title}</h3>
                {/* UPDATE: Change this <p> line to use the truncation function.
                    It now shows only ~50 words + "..." for uniformity. Full description is in details. */}
                <p style={{
                  color: '#666',
                  margin: '0 0 10px 0',
                  lineHeight: '1.4',  // Better readability
                  display: '-webkit-box',  // Optional: Limits to 3 lines visually
                  WebkitLineClamp: 7,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {truncateDescription(course.description)}
                </p>
                <p style={{ color: '#007bff', fontWeight: 'bold' }}>
                  Materials: {course.materials?.length || 0}
                </p>
                <button
                  onClick={() => navigate(`/course/${course.id}`)}
                  style={{
                    background: '#007bff',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    marginTop: '10px'
                  }}
                >
                  Подробнее
                </button>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={() => navigate('/dashboard')}
          style={{
            background: '#28a745',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '5px',
            cursor: 'pointer',
            alignSelf: 'center'
          }}
        >
          На главную
        </button>
      </div>
    </div>
  );
};

export default CourseList;
