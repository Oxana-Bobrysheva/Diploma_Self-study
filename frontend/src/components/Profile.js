import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Profile = () => {
  const [profile, setProfile] = useState({});
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({ name: '', phone: '', city: '', avatar: null });
  const [error, setError] = useState('');
  // New: State for avatar preview URL (for live preview when selecting a new file)
  const [avatarPreview, setAvatarPreview] = useState(null);
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
      // Reset preview when fetching fresh data
      setAvatarPreview(response.data.avatar || null);
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
    // Reset preview to current avatar when starting edit
    setAvatarPreview(profile.avatar || null);
  };

  // Updated: Handle save with FormData for file uploads
  const handleSave = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('No access token found. Please log in.');
      return;
    }
    try {
      let requestData;
      if (formData.avatar && formData.avatar instanceof File) {
        // If avatar is a File, use FormData for multipart upload
        requestData = new FormData();
        requestData.append('name', formData.name);
        requestData.append('phone', formData.phone);
        requestData.append('city', formData.city);
        requestData.append('avatar', formData.avatar);
      } else {
        // Otherwise, send as JSON (for text-only updates)
        requestData = formData;
      }

      const response = await api.put('/users/profiles/me/', requestData, {
        headers: {
          Authorization: `Bearer ${token}`,
          // Set content-type for FormData (axios will auto-set multipart/form-data with boundary)
          ...(formData.avatar && formData.avatar instanceof File ? { 'Content-Type': 'multipart/form-data' } : {}),
        },
      });
      setProfile(response.data);
      setEditing(false);
      // Update preview to the new backend URL
      setAvatarPreview(response.data.avatar || null);
      // Clean up old preview URL if it was a blob
      if (formData.avatar && formData.avatar instanceof File) {
        URL.revokeObjectURL(avatarPreview);
      }
      setError('');
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else {
        setError('Failed to update profile. Check your inputs.');
        console.error('Save error:', err.response?.data); // Log for debugging
      }
    }
  };

  const handleCancel = () => {
    setFormData({
      name: profile.name || '',
      phone: profile.phone || '',
      city: profile.city || '',
      avatar: null  // Reset to no new file
    });
    setAvatarPreview(profile.avatar || null); // Back to original
    setEditing(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Updated: Handle file change with preview
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    console.log('Selected file:', file.name, 'Type:', file.type, 'Size:', file.size); // Debug log

    // Allow common image types explicitly, with a fallback
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type) && !file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение (PNG, JPEG, GIF и т.д.).');
      return;
    }

    if (file.size > 2 * 1024 * 1024) { // 2MB limit
      alert('Файл слишком большой (макс. 2MB).');
      return;
    }

    // Create preview URL for the selected file
    const previewUrl = URL.createObjectURL(file);
    setAvatarPreview(previewUrl);
    setFormData((prev) => ({ ...prev, avatar: file }));
    alert('Аватар выбран успешно!');
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

  // Helper: Get the avatar source (priority: preview if editing and new file, else profile.avatar)
  const getAvatarSrc = () => {
    if (editing && avatarPreview) {
      return avatarPreview; // Show live preview during edit
    }
    return profile.avatar || null;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <button
        onClick={() => navigate('/dashboard')}
        style={{
          backgroundColor: '#28a745',
          color: 'white',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '5px',
          margin: '10px 0',
          cursor: 'pointer'
        }}
      >
        На Главную
      </button>

      <h1 style={{
        color: 'green',
        textAlign: 'center',
        marginBottom: '20px',
        fontSize: '24px'
      }}>
        Это Ваша личная страница, {profile.name}
      </h1>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{
        maxWidth: '600px',
        width: '100%',
        textAlign: 'left',
        margin: '20px 0',
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '100px', height: '100px', borderRadius: '50%', border: '2px solid #ddd' }}>
            {getAvatarSrc() ? (
              <img
                src={getAvatarSrc()}
                alt="Аватар"
                style={{
                  width: '100%',
                  height: '100%',
                  borderRadius: '50%',
                  objectFit: 'cover'
                }}
              />
            ) : (
              <div style={{
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                backgroundColor: '#f0f0f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                color: '#999'
              }}>
                Нет аватара
              </div>
            )}
          </div>

          <div style={{ flex: 1 }}>
            {editing ? (
              <div>

                <label>Имя: <input name="name" value={formData.name} onChange={handleChange} /></label><br />
                <label>Телефон: <input name="phone" value={formData.phone} onChange={handleChange} /></label><br />
                <label>Место проживания: <input name="city" value={formData.city} onChange={handleChange} /></label><br />

                <label>Аватар: <input type="file" accept="image/*" onChange={handleFileChange} /></label><br />

                <button onClick={handleSave}>Сохранить</button>
                <button onClick={handleCancel}>Отменить</button>
              </div>
            ) : (
              <div>
                {/* Removed duplicate avatar display here - now handled in the flex position above */}

                <p><strong>Имя:</strong> {profile.name}</p>
                <p><strong>Email:</strong> {profile.email}</p>
                <p><strong>Телефон:</strong> {profile.phone}</p>
                <p><strong>Место проживания:</strong> {profile.city}</p>
                <p><strong>Роль:</strong> {profile.role}</p>
                <button onClick={handleEdit} style={{
                    backgroundColor: '#007bff',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '5px',
                    marginTop: '10px',
                    marginRight: '10px',
                    cursor: 'pointer'
                  }}
                >Исправить данные профиля</button>
                <button onClick={() => {
                  localStorage.removeItem('access_token');
                  localStorage.removeItem('refresh_token'); // Optional: Also clear refresh token
                  window.location.href = '/';
                }} style={{
                    backgroundColor: '#007bff',
                    color: 'white',
                    padding: '10px 20px',
                    border: 'none',
                    borderRadius: '5px',
                    marginTop: '10px',
                    cursor: 'pointer'
                  }}
                >Выйти</button>
              </div>
            )}
          </div>
        </div>
      </div>

      <h2 style={{ textAlign: 'center', marginTop: '30px' }}>Ваши курсы</h2>

      {(profile.role === 'teacher' || profile.role === 'admin') && (
        <button
          onClick={() => setShowCreateForm(true)}
          style={{ marginBottom: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer' }}
        >
          Создать новый курс
        </button>
      )}

      {showCreateForm && (
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px', backgroundColor: 'white',
        borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
          <h3>Создать новый курс</h3>
          {createError && <p style={{ color: 'red' }}>{createError}</p>}
          <form onSubmit={handleCreateCourse}>
            <label>
              Название:
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
              Описание:
              <textarea
                name="description"
                value={courseData.description}
                onChange={(e) => setCourseData({ ...courseData, description: e.target.value })}
                required
              />
            </label>
            <br />
            <button type="submit">Создать</button>
            <button
              type="button"
              onClick={() => {
                setShowCreateForm(false);
                setCourseData({ title: '', description: '' });
                setCreateError('');
              }}
            >
              Отменить
            </button>
          </form>
        </div>
      )}

      {coursesLoading ? (
        <p>Загружаем курсы...</p>
      ) : coursesError ? (
        <p style={{ color: 'red' }}>{coursesError}</p>
      ) : courses.length === 0 ? (
        <p>No courses enrolled yet.</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginTop: '30px' }}>
          {courses.map((course) => (
            <div key={course.id} style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px',
            backgroundColor: 'white', textAlign: 'center' }}>
              <h3>{course.title}</h3>
              <button
                onClick={() => handleViewCourse(course.id)}
                style={{ backgroundColor: '#007bff', color: 'white', padding: '10px 20px', border: 'none',
                borderRadius: '5px', marginTop: '10px',  textAlign: 'center'}}
              >
                Просмотреть
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Profile;
