// src/components/TeachersList.js
import React, { useState, useEffect } from 'react';

const TeachersList = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/users/teachers/');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        setTeachers(data);
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

  const getInitials = (name) =>
    name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', margin: '20px' }}>
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ margin: '20px', color: 'red', background: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center' }}>Наши авторы</h2>

      <div className="teachers-grid">
        {teachers.map((teacher) => (
          <div key={teacher.id} className="teacher-card">
            {/* Avatar or Initial */}
            <div
              className="avatar"
              style={{
                background: teacher.avatar ? 'none' : '#ff5722',
                border: teacher.avatar ? 'none' : '2px solid #e0e0e0',
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
  );
};

export default TeachersList;
