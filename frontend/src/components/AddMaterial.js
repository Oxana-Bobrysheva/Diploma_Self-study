import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCourseDetails, addMaterial } from '../services/api';  // Path to api.js
import { isAuthenticated, clearTokens } from '../utils/auth';  // For auth checks & clearing on 401

const AddMaterial = () => {
  const { id } = useParams();  // Get course ID from URL (ensure it's valid)
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [courseTitle, setCourseTitle] = useState('');
  const [content, setContent] = useState('');
  const [illustration, setIllustration] = useState(null);
  const [videoLink, setVideoLink] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);  // For both fetch and submit

  useEffect(() => {
    const fetchCourse = async () => {
      if (!isAuthenticated()) {
        setError('Please log in to view this course.');
        navigate('/login');  // Redirect instead of just error
        return;
      }

      setLoading(true);  // Show loading during fetch
      setError('');  // Clear any old errors

      try {
        console.log('Fetching course details...');
        const response = await getCourseDetails(id);  // Axios with auto-token
        console.log('API Response:', response.data);  // Should log full data, no 401
        setCourseTitle(response.data.title || response.data.name || 'Unknown Course');
        // Optional: If you need materials, import & use getMaterials(id) here
      } catch (err) {
        console.error('Fetch error:', err);
        const detail = err.response?.data?.detail || err.response?.data?.message || err.message;
        setError(detail || 'Failed to load course. Please try again.');
        if (err.response?.status === 401) {
          clearTokens();  // Clear invalid tokens
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [id, navigate]);  // Add navigate to deps

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Please enter a title.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content || '');  // Make content optional if empty
    if (illustration) formData.append('illustration', illustration);
    formData.append('video_link', videoLink || '');

    setLoading(true);
    setError('');

    try {
      console.log('Adding material for course', id);
      const response = await addMaterial(id, formData);  // Axios handles token & multipart
      console.log('Material added:', response.data);  // Success log
      alert('Material added successfully! 🎉');
      // Reset form or refetch if needed
      setTitle('');
      setContent('');
      setIllustration(null);
      setVideoLink('');
      navigate(`/courses/${id}`);  // Back to course detail
    } catch (err) {
      console.error('Add material error:', err);
      const detail = err.response?.data?.detail || err.response?.data?.message || err.message;
      setError(detail || 'Failed to add material. Check fields, permissions, or try again.');
      if (err.response?.status === 401) {
        clearTokens();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  // Early return if loading the course
  if (loading && !courseTitle) {
    return <div>Loading course details...</div>;  // Simple spinner or your UI
  }

  return (
    <div>
      <h2>Add Material to Course: {courseTitle || 'Loading...'}</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Название:
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>
        <br />

        <label>
          Содержание:
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows="4"
          />
        </label>
        <br />
        <label>
          Иллюстрация:
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setIllustration(e.target.files[0])}
          />
        </label>
        <br />
        <label>
          Ссылка на видео:
          <input
            type="url"
            value={videoLink}
            onChange={(e) => setVideoLink(e.target.value)}
            placeholder="https://..."
          />
        </label>
        <br />
        <button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Добавить'}
        </button>
        <button type="button" onClick={() => navigate(`/courses/${id}`)} disabled={loading}>
          Отменить
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default AddMaterial;
