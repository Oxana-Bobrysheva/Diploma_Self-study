import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { getCourses } from '../services/api';
import { isAuthenticated, clearTokens } from '../utils/auth';

const Dashboard = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    } else {
      getCourses()
        .then(response => {
          setCourses(response.data);
          setLoading(false);
        })
        .catch(() => {
          navigate('/login');
        });
    }
  }, [navigate]);

  const handleLogout = () => {
    clearTokens();
    navigate('/login');
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Dashboard</h2>
      <button onClick={handleLogout} style={{ padding: '10px', marginBottom: '20px' }}>Logout</button>
      <h3>Your Courses</h3>
      <Link to="/courses">View All Courses</Link>
      <ul>
        {courses.length > 0 ? (
          courses.map(course => (
            <li key={course.id} style={{ margin: '10px 0' }}>
              {course.title} - {course.description}
            </li>
          ))
        ) : (
          <p>No courses available yet. Create some in the Django admin!</p>
        )}
      </ul>
    </div>
  );
};

export default Dashboard;
