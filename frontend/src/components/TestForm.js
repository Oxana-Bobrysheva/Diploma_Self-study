import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';
import { getTests, getTestDetails, submitTestResult } from '../services/api';

const TestForm = () => {
  const { courseId } = useParams();
  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    } else {
      getTests(courseId)
        .then(response => {
          setTests(response.data);
          setLoading(false);
        })
        .catch(() => {
          navigate('/login');
        });
    }
  }, [courseId, navigate]);

  const handleTestClick = async (testId) => {
    const response = await getTestDetails(testId);
    setSelectedTest(response.data);
    // Initialize answers object with question IDs
    const initialAnswers = {};
    response.data.questions.forEach(q => initialAnswers[q.id] = '');
    setAnswers(initialAnswers);
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await submitTestResult({
        test: selectedTest.id,
        answers: answers,
        score: 0  // Backend can calculate score; for now, send 0
      });
      alert('Test submitted!');
      setSelectedTest(null);
    } catch (err) {
      alert('Submission failed');
    }
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading tests...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Tests for Course {courseId}</h2>
      <ul>
        {tests.map(test => (
          <li key={test.id} style={{ margin: '10px 0' }}>
            <button onClick={() => handleTestClick(test.id)}>{test.title}</button>
          </li>
        ))}
      </ul>
      {selectedTest && (
        <form onSubmit={handleSubmit} style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
          <h3>{selectedTest.title}</h3>
          {selectedTest.questions.map(question => (
            <div key={question.id} style={{ margin: '10px 0' }}>
              <p>{question.text}</p>
              <input
                type="text"
                value={answers[question.id]}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
          ))}
          <button type="submit">Submit Test</button>
        </form>
      )}
      <Link to={`/course/${courseId}/materials`}>View Materials</Link> | <Link to="/courses">Back to Courses</Link>
    </div>
  );
};

export default TestForm;
