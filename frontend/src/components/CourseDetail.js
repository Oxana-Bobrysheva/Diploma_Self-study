import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';  // Adjust path if needed

const CourseDetail = () => {
  const { id } = useParams();  // Get course ID from URL
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [profile, setProfile] = useState(null);
  const [isOwner, setIsOwner] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  // New: States for inline editing
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [hasAccess, setHasAccess] = useState(false);
  const [formData, setFormData] = useState({title: '', content: ''});
  const [showAddForm, setShowAddForm] = useState(false);

   // New: Fetch user profile to get role
  const fetchProfile = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    try {
      const response = await api.get('/users/profiles/me/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (err) {
      console.error('Failed to fetch profile:', err);
      return null;
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      console.log('fetchData is starting...');
      const token = localStorage.getItem('access_token');
      console.log('Access Token:', token ? 'Present (not empty)' : 'NULL or MISSING!');
      if (!token) {
        console.error('No token found—redirecting to login');
        setError('No access token found. Please log in.');
        setLoading(false);
        return;
      }
      console.log('Token is valid—proceeding with API calls');
      try {
        // CHANGE: Fetch profile and course in parallel (this was already here, but now fully inside try)
        const [profileData, courseResponse] = await Promise.all([
          fetchProfile(),
          api.get(`/courses/${id}/`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

        // CHANGE: Set states first (using fetched data)
        setProfile(profileData);
        setCourse(courseResponse.data);

        const isOwner = profileData?.id === courseResponse.data?.owner;
        const isTeacher = profileData?.role === 'teacher';
        const isAdmin = profileData?.role === 'admin';

// Set hasAccess based on roles
        setHasAccess(isAdmin || isTeacher || isOwner);
        console.log('Profile:', profileData);
        console.log('Course:', courseResponse.data);
        console.log('isTeacherOrAdmin:', profileData?.role === 'teacher' || profileData?.role === 'admin');

        // CHANGE: Initialize edit states with course data (moved here after setCourse for safety)
        setEditTitle(courseResponse.data.title);
        setEditDescription(courseResponse.data.description);
        console.log('Course data:', courseResponse.data);  // Debug log

        const isOwnerCheck = profileData?.id === courseResponse.data?.owner;  // Direct ID comparison (owner field)
        console.log('isOwner check (profile.id === course.owner):', isOwnerCheck);
        setIsOwner(isOwnerCheck);  // Set the state (add && (profileData?.role === 'teacher') if role needed)

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

    fetchData();
  }, [id, navigate]);

  const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const res = await fetch(`/api/courses/${id}/add-material/`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ courseId: course.id, ...formData })
    });

    if (!res.ok) {
      if (res.status === 403) {
        alert('Access denied. You can’t add materials here.');
      } else {
        alert('Failed to save.');
      }
      return;
    }

    // Success — close form, refresh data, etc.
    setShowAddForm(false);
  } catch (err) {
    alert('Network error.');
  }
};

  // New: Handle enrollment for students
  const handleEnroll = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    try {
      await api.post(`/courses/${id}/enroll/`, {}, {  // Adjust endpoint if needed
        headers: { Authorization: `Bearer ${token}` },
      });
      alert('Successfully enrolled in the course!');
      // Refresh course data after enrollment
      const response = await api.get(`/courses/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCourse(response.data);
    } catch (err) {
      console.error('Enrollment error:', err);
      alert('Failed to enroll. You might already be enrolled.');
    }
  };

  // New: Handle saving edits
  const handleSaveEdit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    try {
      await api.patch(`/courses/${id}/edit/`, { title: editTitle, description: editDescription }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCourse({ ...course, title: editTitle, description: editDescription });  // Update local state
      setEditing(false);
      alert('Course updated successfully!');
    } catch (err) {
      console.error('Edit error:', err);
      alert('Failed to update course.');
    }
  };

  // NOTE: If enrolled_students is array of objects, change to .some(student => student.id === profile?.id)
  const isEnrolled = profile && course?.enrolled_students?.includes(profile.id);

  // CHANGE: Keep isTeacherOrAdmin for other logic, but DON'T redefine isOwner here (use state instead)
  const isTeacherOrAdmin = profile?.role === 'teacher' || profile?.role === 'admin';

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
        padding: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <p>Loading course details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <p style={{ color: 'red' }}>{error}</p>
        <button
          onClick={() => navigate('/profile')}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Вернуться в профиль
        </button>
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <p>Course not found.</p>
        <button
          onClick={() => navigate('/profile')}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Вернуться в профиль
        </button>
      </div>
    );
  }

  // Determine user role and ownership
  // CHANGE: Use state isOwner here (no redefinition—prevents shadowing and timing issues)
  // NOTE: If you want role check in UI, change to: isOwner && isTeacherOrAdmin

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
      display: 'flex'  // Flex layout for sidebar + main content
    }}>
      {/* Left Sidebar */}
      <div style={{
        width: '250px',  // Fixed width for sidebar
        backgroundColor: '#aaaaaa',  // Light gray background
        padding: '20px',
        boxShadow: '2px 0 5px rgba(0,0,0,0.1)',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        <button
        onClick={() => navigate('/dashboard')}
        style={{
          background: '#28a745',
          color: 'white',
          border: 'none',
          padding: '12px 24px',
          borderRadius: '5px',
          cursor: 'pointer',
          alignSelf: 'centre',
          marginBottom: '20px'
        }}
      >
        На главную
      </button>
        <button
          onClick={() => navigate('/profile')}
          style={{
            backgroundColor: '#ffffff',
            color: 'green',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Вернуться в профиль
        </button>
        {/* Role-Based Buttons in Sidebar */}
        {/* CHANGE: Use state isOwner (and optionally && isTeacherOrAdmin) for condition */}
        {isOwner && (
          <>
            <button
              onClick={() => setEditing(true)}
              style={{
            backgroundColor: '#ffffff',
            color: 'green',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
            >
              Редактировать курс
            </button>
            {hasAccess && (
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-500 text-white px-4 py-2 rounded"
              style={{
                backgroundColor: '#ffffff',
                color: 'green',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
            Добавить материал
          </button>
        )}
            <button
              onClick={() => navigate(`/courses/${id}/students`)}
              style={{
            backgroundColor: '#ffffff',
            color: 'green',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
            >
              Просмотр зачисленных студентов
            </button>
          </>
        )}
      </div>

      {/* Main Content Area */}
      <div style={{
        flex: 1,  // Takes remaining space
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        {/* Conditional Rendering: View Mode or Edit Mode */}
        {editing ? (
          // Edit Mode
          <div style={{
            maxWidth: '800px',
            width: '100%',
            padding: '20px',
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <h2>Редактировать курс</h2>
            <form onSubmit={handleSaveEdit}>
              <label>Название:</label>
              <input
                type="text"
                placeholder="Material title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
              <textarea
                placeholder="Content"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              />
              <button type="submit" style={{
                backgroundColor: '#28a745',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                marginRight: '10px'
              }}>
                Сохранить
              </button>
              <button type="button" onClick={() => {
                setEditing(false);
                setEditTitle(course.title);
                setEditDescription(course.description);
              }} style={{
                backgroundColor: '#6c757d',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}>
                Отменить
              </button>
            </form>
          </div>
        ) : (
          // View Mode
          <>
            <h1 style={{
              color: 'green',
              textAlign: 'center',
              marginBottom: '20px',
              fontSize: '32px'
            }}>
              {course.title}
            </h1>
            {/* Course Description */}
            <div style={{
              maxWidth: '800px',
              width: '100%',
              padding: '20px',
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              marginBottom: '20px'
            }}>
              <h2>Описание</h2>
              <p>{course.description}</p>
            </div>
          </>
        )}

        {showAddForm && (
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            zIndex: 1000
          }}>
            <form onSubmit={handleSubmit}>
              <h3>Добавить материал</h3>
              <input
                type="text"
                placeholder="Название материала"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
                required
              />
              <textarea
                placeholder="Содержание"
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                style={{ width: '100%', padding: '8px', marginBottom: '10px', minHeight: '100px' }}
                required
              />
              <button type="submit" style={{
                backgroundColor: '#28a745',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                marginRight: '10px'
              }}>
                Сохранить
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setFormData({ title: '', content: '' });
                }}
                style={{
                  backgroundColor: '#6c757d',
                  color: 'white',
                  padding: '10px 20px',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
              >
                Закрыть
              </button>
            </form>
          </div>
        )}

        {/* Role-Based Actions for Students (Enroll Button) */}
        {/* CHANGE: Use isTeacherOrAdmin (kept as-is; no change to isOwner here) */}
        {!isTeacherOrAdmin && !isEnrolled && (
          <button
            onClick={handleEnroll}
            style={{
              backgroundColor: '#007bff',
              color: 'white',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Записаться на курс
          </button>
        )}
      </div>
    </div>
  );
};

export default CourseDetail;
