import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';
import { getMaterials, getMaterialDetails } from '../services/api';

const MaterialViewer = () => {
  const { courseId } = useParams();
  const [materials, setMaterials] = useState([]);
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    } else {
      getMaterials(courseId)
        .then(response => {
          setMaterials(response.data);
          setLoading(false);
        })
        .catch(() => {
          navigate('/login');
        });
    }
  }, [courseId, navigate]);

  const handleMaterialClick = async (materialId) => {
    const response = await getMaterialDetails(materialId);
    setSelectedMaterial(response.data);
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading materials...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Materials for Course {courseId}</h2>
      <ul>
        {materials.map(material => (
          <li key={material.id} style={{ margin: '10px 0' }}>
            <button onClick={() => handleMaterialClick(material.id)}>{material.title}</button>
          </li>
        ))}
      </ul>
      {selectedMaterial && (
        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
          <h3>{selectedMaterial.title}</h3>
          <p>{selectedMaterial.content}</p>
          <p><strong>Materials:</strong> {selectedMaterial.materials || 'None'}</p>
        </div>
      )}
      <Link to={`/course/${courseId}/tests`}>View Tests</Link> | <Link to="/courses">Back to Courses</Link>
    </div>
  );
};

export default MaterialViewer;
