import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getTeachers } from '../services/api';

const TeachersList = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Helper function (must be outside JSX)
  const getInitials = (name) =>
    name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2);

  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const response = await getTeachers();
        setTeachers(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching teachers:', err);
        setError('Failed to load teachers. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    fetchTeachers();
  }, []);

  // Single return statement for the entire component
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      {/* Back to Dashboard Button */}
      <button
        onClick={() => navigate('/')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '10px 20px',
          backgroundColor: '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          marginBottom: '24px',
          fontWeight: 500,
          transition: 'background-color 0.3s'
        }}
        type="button"
      >
        На главную
      </button>

      {/* Loading State */}
      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '20px' }}>
          <div className="spinner"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div
          style={{
            margin: '20px',
            color: 'red',
            background: '#ffe6e6',
            padding: '10px',
            borderRadius: '4px'
          }}
        >
          {error}
        </div>
      )}

      {/* Teachers List (only if not loading/error) */}
      {!loading && !error && (
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ color: 'green', textAlign: 'center', marginBottom: '10px' }}>Наши авторы</h1>

          <div className="teachers-grid">
            {teachers.map((teacher) => (
              <div key={teacher.id} className="teacher-card">
                {/* Avatar or Initial */}
                <div
                  className="avatar"
                  style={{
                    background: teacher.avatar ? 'none' : '#ff5722',
                    border: teacher.avatar ? 'none' : '2px solid #e0e0e0'
                  }}
                >
                  {teacher.avatar ? (
                    <img src={teacher.avatar} alt={teacher.name} />
                  ) : (
                    getInitials(teacher.name)
                  )}
                </div>

                {/* Name */}
                <h3 style={{ margin: '10px 0', fontSize: '18px' }}>{teacher.name}</h3>

                {/* Courses */}
                <div style={{ fontStyle: 'italic', color: '#666', marginBottom: '8px' }}>Курсы:</div>
                <ul style={{ margin: 0, paddingLeft: '16px' }}>
                  {teacher.courses.length > 0 ? (
                    teacher.courses.map((course) => (
                      <li key={course.id} style={{ marginBottom: '4px' }}>
                        {course.title}
                      </li>
                    ))
                  ) : (
                    <li style={{ color: '#999' }}>Нет назначенных курсов</li>
                  )}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TeachersList;
