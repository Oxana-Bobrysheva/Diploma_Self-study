import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCourseDetails, addMaterial } from '../services/api';
import { isAuthenticated, clearTokens } from '../utils/auth';

const AddMaterial = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [courseTitle, setCourseTitle] = useState('');
  const [courseOwner, setCourseOwner] = useState(null);
  const [content, setContent] = useState('');
  const [illustration, setIllustration] = useState(null);
  const [videoLink, setVideoLink] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [courseLoading, setCourseLoading] = useState(true);
  const [userInfo, setUserInfo] = useState({ id: '', role: '' });

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

        // Получаем информацию о пользователе из токена
        const token = localStorage.getItem('access_token');
        if (token) {
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            setUserInfo({
              id: payload.user_id,
              role: payload.role || 'student'
            });
            console.log('👤 Current user:', payload);
          } catch (e) {
            console.error('❌ Error parsing token:', e);
          }
        }

        // Получаем информацию о владельце курса
        const owner = courseData.owner;
        setCourseOwner(owner);
        console.log('👨‍🏫 Course owner:', owner);

        // Проверяем права доступа
        if (owner && owner.id !== userInfo.id && userInfo.role !== 'admin') {
          setError('У вас нет прав для добавления материалов к этому курсу. Только владелец курса или администратор могут добавлять материалы.');
        }

        // Получаем название курса
        const foundTitle = courseData.title || courseData.name || 'Неизвестный курс';
        setCourseTitle(foundTitle);

      } catch (err) {
        console.error('❌ Fetch course error:', err);

        if (err.response?.status === 404) {
          setError('Курс не найден. Проверьте ID курса.');
        } else if (err.response?.status === 401) {
          setError('Сессия истекла. Пожалуйста, войдите снова.');
          clearTokens();
          navigate('/login');
        } else if (err.response?.status === 403) {
          setError('Доступ запрещен. У вас нет прав для просмотра этого курса.');
        } else {
          const detail = err.response?.data?.detail ||
                        err.response?.data?.message ||
                        err.message ||
                        'Не удалось загрузить информацию о курсе.';
          setError(detail);
        }
      } finally {
        setCourseLoading(false);
      }
    };

    if (courseId) {
      fetchCourse();
    } else {
      setError('ID курса не указан.');
      setCourseLoading(false);
    }
  }, [courseId, navigate, userInfo.id]);

  const checkPermissions = () => {
    // Админы могут всё
    if (userInfo.role === 'admin') return true;

    // Владельцы курса могут добавлять материалы
    if (courseOwner && courseOwner.id === userInfo.id) return true;

    // Учителя могут добавлять материалы к своим курсам
    if (userInfo.role === 'teacher' && courseOwner && courseOwner.id === userInfo.id) return true;

    return false;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Проверяем права доступа
    if (!checkPermissions()) {
      setError('У вас нет прав для добавления материалов к этому курсу. Только владелец курса или администратор могут добавлять материалы.');
      return;
    }

    if (!title.trim()) {
      setError('Пожалуйста, введите название материала.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content || '');
    if (illustration) {
      formData.append('illustration', illustration);
      console.log('📎 Added illustration file:', illustration.name);
    }
    formData.append('video_link', videoLink || '');

    // Логируем данные формы для отладки
    console.log('📤 Submitting form data:');
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value);
    }

    setLoading(true);
    setError('');

    try {
      console.log('🔄 Adding material for course', courseId);
      const response = await addMaterial(courseId, formData);
      console.log('✅ Material added successfully:', response.data);
      alert('Материал успешно добавлен! 🎉');

      // Сброс формы
      setTitle('');
      setContent('');
      setIllustration(null);
      setVideoLink('');

      // Возврат к деталям курса
      navigate(`/courses/${courseId}`);
    } catch (err) {
      console.error('❌ Add material error:', err);
      console.error('Error response:', err.response);

      let errorMessage = 'Не удалось добавить материал. ';

      if (err.response?.status === 401) {
        errorMessage += 'Сессия истекла. Пожалуйста, войдите снова.';
        clearTokens();
        navigate('/login');
      } else if (err.response?.status === 403) {
        errorMessage += 'У вас нет прав для добавления материалов к этому курсу. Только владелец курса или администратор могут добавлять материалы.';
      } else if (err.response?.data) {
        // Обрабатываем ошибки валидации Django
        const errorData = err.response.data;
        if (typeof errorData === 'object') {
          const validationErrors = [];
          for (const [field, messages] of Object.entries(errorData)) {
            validationErrors.push(`${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`);
          }
          errorMessage += validationErrors.join('; ');
        } else {
          errorMessage += errorData.detail || errorData.message || JSON.stringify(errorData);
        }
      } else {
        errorMessage += 'Проверьте подключение к интернету и попробуйте снова.';
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Если загружается информация о курсе
  if (courseLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div className="spinner" style={{ marginBottom: '20px' }}></div>
        <p style={{ fontSize: '18px', color: '#666' }}>Загрузка информации о курсе...</p>
      </div>
    );
  }

  const hasPermission = checkPermissions();

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',
      padding: '20px'
    }}>
      {/* Кнопка назад */}
      <button
        onClick={() => navigate(`/courses/${courseId}`)}
        style={{
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '5px',
          marginBottom: '20px',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        ← Назад к курсу
      </button>

      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{
          color: 'green',
          textAlign: 'center',
          marginBottom: '10px',
          fontSize: '28px'
        }}>
          Добавить материал
        </h1>

        <div style={{
          textAlign: 'center',
          marginBottom: '30px',
          padding: '15px',
          backgroundColor: '#f8f9fa',
          borderRadius: '6px',
          border: '1px solid #e9ecef'
        }}>
          <h2 style={{
            color: '#495057',
            margin: '0',
            fontSize: '20px'
          }}>
            Курс: <span style={{ color: 'green', fontWeight: 'bold' }}>{courseTitle}</span>
          </h2>
          {courseOwner && (
            <p style={{
              color: '#6c757d',
              margin: '5px 0 0 0',
              fontSize: '14px'
            }}>
              Владелец курса: {courseOwner.name || courseOwner.email} (ID: {courseOwner.id}) |
              Ваша роль: {userInfo.role} | Ваш ID: {userInfo.id}
            </p>
          )}
        </div>

        {!hasPermission && (
          <div style={{
            color: '#856404',
            backgroundColor: '#fff3cd',
            padding: '15px',
            borderRadius: '4px',
            marginBottom: '20px',
            textAlign: 'center',
            border: '1px solid #ffeaa7'
          }}>
            <strong>Внимание:</strong> У вас нет прав для добавления материалов к этому курсу.
            Только владелец курса или администратор могут добавлять материалы.
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#495057' }}>
              Название материала: *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              disabled={!hasPermission || loading}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '16px',
                boxSizing: 'border-box',
                opacity: hasPermission ? 1 : 0.6
              }}
              placeholder="Введите название материала"
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#495057' }}>
              Содержание:
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows="6"
              disabled={!hasPermission || loading}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '16px',
                resize: 'vertical',
                boxSizing: 'border-box',
                fontFamily: 'inherit',
                opacity: hasPermission ? 1 : 0.6
              }}
              placeholder="Опишите содержание материала..."
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#495057' }}>
              Иллюстрация:
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files[0];
                setIllustration(file);
                console.log('📁 Selected file:', file);
              }}
              disabled={!hasPermission || loading}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                boxSizing: 'border-box',
                opacity: hasPermission ? 1 : 0.6
              }}
            />
            <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
              Поддерживаемые форматы: JPG, PNG, GIF, WEBP (макс. 5MB)
            </small>
          </div>

          <div style={{ marginBottom: '30px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#495057' }}>
              Ссылка на видео:
            </label>
            <input
              type="url"
              value={videoLink}
              onChange={(e) => setVideoLink(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              disabled={!hasPermission || loading}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '16px',
                boxSizing: 'border-box',
                opacity: hasPermission ? 1 : 0.6
              }}
            />
          </div>

          {error && (
            <div style={{
              color: '#dc3545',
              backgroundColor: '#f8d7da',
              padding: '15px',
              borderRadius: '4px',
              marginBottom: '20px',
              textAlign: 'center',
              border: '1px solid #f5c6cb'
            }}>
              <strong>Ошибка:</strong> {error}
            </div>
          )}

          <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              type="submit"
              disabled={!hasPermission || loading}
              style={{
                backgroundColor: !hasPermission ? '#6c757d' : (loading ? '#6c757d' : '#28a745'),
                color: 'white',
                border: 'none',
                padding: '12px 30px',
                borderRadius: '5px',
                cursor: (hasPermission && !loading) ? 'pointer' : 'not-allowed',
                fontSize: '16px',
                minWidth: '160px'
              }}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{
                    width: '20px',
                    height: '20px',
                    display: 'inline-block',
                    marginRight: '8px',
                    borderWidth: '2px'
                  }}></div>
                  Добавление...
                </>
              ) : (
                hasPermission ? 'Добавить материал' : 'Нет прав доступа'
              )}
            </button>

            <button
              type="button"
              onClick={() => navigate(`/courses/${courseId}`)}
              disabled={loading}
              style={{
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                padding: '12px 30px',
                borderRadius: '5px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                minWidth: '120px'
              }}
            >
              Отменить
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddMaterial;