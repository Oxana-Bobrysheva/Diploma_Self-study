import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';
import { getCourses } from '../services/api';

const CourseList = () => {
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

  if (loading) return <div style={{ padding: '20px' }}>Loading courses...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Courses</h2>
      <ul>
        {courses.length > 0 ? (
          courses.map(course => (
            <li key={course.id} style={{ margin: '10px 0' }}>
              <strong>{course.title}</strong> - {course.description}
              <br />
              <Link to={`/course/${course.id}/materials`}>View Materials</Link> |
              <Link to={`/course/${course.id}/tests`}>View Tests</Link>
            </li>
          ))
        ) : (
          <p>No courses available yet.</p>
        )}
      </ul>
      <Link to="/dashboard">Back to Dashboard</Link>
    </div>
  );
};

export default CourseList;
