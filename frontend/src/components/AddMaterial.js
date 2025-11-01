import React, { useState, useEffect, useCallback } from 'react';  // Added useCallback
import { useParams, useNavigate } from 'react-router-dom';
import { addMaterial } from '../services/api';  // Assuming your API service
import { getCourseDetails } from '../services/api';  // Your course API
// Fixed import: Assuming 'api' is the default export (your Axios instance)
import api from '../services/api';

const AddMaterial = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();

  // States
  const [courseLoading, setCourseLoading] = useState(true);
  const [error, setError] = useState('');
  const [courseTitle, setCourseTitle] = useState('');
  const [courseOwner, setCourseOwner] = useState(null);
  const [userInfo, setUserInfo] = useState({ id: '', role: 'student' });
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    file: null,
  });
  const [submitLoading, setSubmitLoading] = useState(false);

  // Helper: Check if authenticated (assuming you have this)
  const isAuthenticated = () => {
    const token = localStorage.getItem('access_token');
    return !!token;
  };

  // Updated: Fetch user profile for role
  const getUserProfile = async (userId) => {
    const token = localStorage.getItem('access_token');
    return api.get(`/users/${userId}/`, {  // Adjust endpoint to your backend (e.g., /api/users/{id}/)
      headers: { Authorization: `Bearer ${token}` }
    });
  };

  // Updated checkPermissions with useCallback to fix ESLint warning
  const checkPermissions = useCallback(() => {
    console.log('🔐 Checking permissions...');
    console.log('User Info:', userInfo);
    console.log('Course Owner (raw):', courseOwner, typeof courseOwner);

    // Админы могут всё
    if (userInfo.role === 'admin') {
      console.log('✅ Access granted: User is admin');
      return true;
    }

    // Нормализуем courseOwner: если это просто ID (number/string), сделаем объектом {id: owner}
    let normalizedOwner = courseOwner;
    if (typeof courseOwner === 'number' || typeof courseOwner === 'string') {
      normalizedOwner = { id: courseOwner };
      console.log('🔄 Normalized owner to object:', normalizedOwner);
    }

    // Теперь проверяем
    if (normalizedOwner && normalizedOwner.id) {
      // Владельцы курса могут добавлять материалы (ID match)
      if (String(normalizedOwner.id) === String(userInfo.id)) {
        console.log('✅ Access granted: User is course owner (ID match)');
        return true;
      }
      // Учителя могут добавлять материалы к своим курсам
      if (String(normalizedOwner.id) === String(userInfo.id)) {
        console.log('✅ Access granted: User is teacher and course owner');
        return true;
      }
    } else {
      console.log('❌ Course owner not properly defined');
    }

    console.log('❌ Access denied: No matching permissions');
    return false;
  }, [userInfo, courseOwner]);  // Deps: userInfo and courseOwner

  // Updated useEffect: Fetch course + user profile (checkPermissions NOT in deps to prevent loop)
  useEffect(() => {
  const fetchCourse = async () => {
    if (!isAuthenticated()) {
      setError('Пожалуйста, войдите в систему для просмотра этого курса.');
      navigate('/login');
      return;
    }

    setCourseLoading(true);
    setError('');
    try {
      console.log('🔄 Fetching course details for course ID:', courseId);
      const response = await getCourseDetails(courseId);
      console.log('✅ Course API Response:', response.data);

      const courseData = response.data;

      // Получаем информацию о пользователе из токена (только ID, так как role нет в JWT)
      const token = localStorage.getItem('access_token');
      let userId = '';
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          userId = payload.user?.id || '';
          console.log('👤 JWT Payload (ID only):', { userId });
        } catch (e) {
          console.error('❌ Error parsing token:', e);
        }
      }

      // Fetch full user profile to get role
      let userRole = 'student';  // Default
      let userName = '';  // Optional
      let userEmail = '';
      if (userId) {
        try {
          const userResponse = await getUserProfile(userId);
          console.log('👤 User Profile Response:', userResponse.data);
          const userData = userResponse.data;
          userRole = userData.role || 'student';
          userName = userData.name || '';
          userEmail = userData.email || '';
        } catch (profileErr) {
          console.error('❌ Error fetching user profile:', profileErr);
        }
      }

      // Set user info with fetched role
      setUserInfo({
        id: userId,
        role: userRole
      });
      console.log('👤 Final User Info:', { id: userId, role: userRole, name: userName || userEmail });


      // Получаем информацию о владельце курса (может быть ID или объектом)
      const owner = courseData.owner;
      setCourseOwner(owner);
      console.log('👨‍🏫 Course owner (raw):', owner, typeof owner);


      // Set course title
      setCourseTitle(courseData.title || 'Неизвестный курс');

    } catch (err) {
      console.error('❌ Error fetching course:', err);
      setError('Ошибка при загрузке данных курса. Попробуйте позже.');
      if (err.response?.status === 403 || err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setCourseLoading(false);
    }
  };

  fetchCourse();
}, [courseId, navigate]);

  // Form handlers (assuming your original logic)
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData((prev) => ({ ...prev, file: e.target.files[0] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!checkPermissions()) {
      setError('У вас нет прав для добавления материалов.');
      return;
    }

    setSubmitLoading(true);
    setError('');
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('description', formData.description);
      if (formData.file) {
        formDataToSend.append('file', formData.file);
      }
      formDataToSend.append('course', courseId);

      const response = await addMaterial(formDataToSend);
      console.log('✅ Material added:', response.data);
      alert('Материал успешно добавлен!');  // Or use a toast
      setFormData({ title: '', description: '', file: null });  // Reset form
      // Optionally navigate or refresh
    } catch (err) {
      console.error('❌ Error adding material:', err);
      setError('Ошибка при добавлении материала. Проверьте данные и попробуйте снова.');
    } finally {
      setSubmitLoading(false);
    }
  };

  if (courseLoading) {
    return <div>Загрузка курса...</div>;
  }

  const hasPermissions = checkPermissions();

  return (
    <div className="add-material-container">
      <h1>Добавить материал к курсу</h1>

      {error && <div className="error">{error}</div>}

      {courseTitle && (
        <div className="course-info">
          <h2>Курс: {courseTitle}</h2>
          {courseOwner && (
            <p>
              Владелец курса: {typeof courseOwner === 'object' ? (courseOwner.name || courseOwner.email || 'Неизвестно') : `ID ${courseOwner}`} (ID: {typeof courseOwner === 'object' ? courseOwner.id : courseOwner}) |
              Ваша роль: {userInfo.role} | Ваш ID: {userInfo.id}
            </p>
          )}
          {!hasPermissions && <p className="no-permissions">Нет прав для добавления материалов.</p>}
        </div>
      )}

      {hasPermissions && (
        <form onSubmit={handleSubmit} encType="multipart/form-data">
          <div className="form-group">
            <label>Название материала:</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Описание:</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}  // FIXED: Was 'handleFormData' – now 'handleInputChange'
              rows="4"
            />
          </div>

          <div className="form-group">
            <label>Файл:</label>
            <input
              type="file"
              name="file"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.png"  // Adjust as needed
            />
          </div>

          <button type="submit" disabled={submitLoading}>
            {submitLoading ? 'Добавление...' : 'Добавить материал'}
          </button>
        </form>
      )}

      <style jsx>{`
        .add-material-container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .error { color: red; background: #ffe6e6; padding: 10px; border-radius: 4px; }
        .course-info { background: #f0f8ff; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .no-permissions { color: orange; font-weight: bold; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:disabled { background: #ccc; cursor: not-allowed; }
      `}</style>
    </div>
  );
};

export default AddMaterial;
