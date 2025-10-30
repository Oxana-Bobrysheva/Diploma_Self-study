import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { addMaterial } from '../services/api';  // Import the helper (adjust path if needed)

const AddMaterial = () => {
  const { id } = useParams();  // Get course ID from URL
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [price, setPrice] = useState(0.00);
  const [content, setContent] = useState('');
  const [illustration, setIllustration] = useState(null);
  const [videoLink, setVideoLink] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);  // Optional: for UX

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', title);
    formData.append('price', price);
    formData.append('content', content);
    if (illustration) formData.append('illustration', illustration);
    formData.append('video_link', videoLink || '');

    setLoading(true);
    setError('');
    try {
      await addMaterial(id, formData);  // Use the helper!
      alert('Material added successfully! 🎉');
      navigate(`/courses/${id}`);  // Back to course detail
    } catch (err) {
      console.error('Add material error:', err);
      setError('Failed to add material. Check fields, permissions, or try again.');
    } finally {
      setLoading(false);
    }
  };

  // Rest of your form JSX stays the same...
  return (
    <div>
      <h2>Add Material to Course {id}</h2>
      <form onSubmit={handleSubmit}>
        {/* Your inputs for title, price, content, illustration, videoLink */}
        <label>
          Title:
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </label>
        <br />
        <label>
          Price (RUB):
          <input type="number" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} min="0" />
        </label>
        <br />
        <label>
          Content:
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows="4" />
        </label>
        <br />
        <label>
          Illustration:
          <input type="file" accept="image/*" onChange={(e) => setIllustration(e.target.files[0])} />
        </label>
        <br />
        <label>
          Video Link:
          <input type="url" value={videoLink} onChange={(e) => setVideoLink(e.target.value)} placeholder="https://..." />
        </label>
        <br />
        <button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Material'}
        </button>
        <button type="button" onClick={() => navigate(`/courses/${id}`)}>Cancel</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default AddMaterial;
