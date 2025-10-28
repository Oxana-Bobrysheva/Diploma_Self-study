import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('access_token');
    const isLoggedIn = !!token;

    // State for statistics
    const [totalCourses, setTotalCourses] = useState(0);
    const [totalAuthors, setTotalAuthors] = useState(0);
    const [loading, setLoading] = useState(true);

    // Fetch stats on component mount

useEffect(() => {
  const fetchStats = async () => {
    try {
      // Fetch courses
      const coursesResponse = await axios.get('/api/courses/', {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      setTotalCourses(coursesResponse.data.length);

      // Fetch authors count (fixed!)
      const authorsResponse = await axios.get('/api/users/authors-count/');
      setTotalAuthors(authorsResponse.data.count);

    } catch (error) {
      console.error('Error fetching stats:', error);
      setTotalAuthors(0); // Fallback on error
    } finally {
      setLoading(false);
    }
  };

  fetchStats();
}, [token]);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/');
        window.location.reload();
    };

    // Reusable button style for links
    const buttonStyle = {
        backgroundColor: 'white',
        color: '#001F3F',  // Dark blue
        border: 'none',
        padding: '10px 15px',
        borderRadius: '8px',  // Rounded
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',  // Subtle shadow
        textDecoration: 'none',
        display: 'inline-block',
        cursor: 'pointer',
        fontSize: '16px',
        transition: 'transform 0.2s, box-shadow 0.2s',  // Smooth hover
        margin: '0 5px'
    };

    // Hover handler functions (no need for hoverStyle object since we handle it here)
    const handleMouseEnter = (e) => {
        e.target.style.transform = 'scale(1.05)';
        e.target.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
    };

    const handleMouseLeave = (e) => {
        e.target.style.transform = 'scale(1)';
        e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
    };

    return (
        <div style={{
            padding: '20px',
            background: 'linear-gradient(to bottom, #FFF9E6, #FFEFD5)',  // Pale yellow gradient for memorization
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',  // Centers horizontally
            // Removed justifyContent: 'center' to avoid vertical centering
            textAlign: 'center',
            color: '#333'  // Dark text for contrast on yellow bg
        }}>
            {/* Header with Navigation Buttons */}
            <header style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                width: '100%',
                maxWidth: '1200px',
                marginBottom: '20px'  // Space from welcome
            }}>
                <nav>
                    <ul style={{ display: 'flex', listStyle: 'none', gap: '10px', padding: 0, margin: 0 }}>
                        <li>
                            <Link
                                to="/courses"
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Курсы
                            </Link>
                        </li>
                        <li>
                            <Link
                                to="/teachers"
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Авторы
                            </Link>
                        </li>
                        <li>
                            <Link
                                to="/blog"
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Обсуждения
                            </Link>
                        </li>
                    </ul>
                </nav>
                <div>
                    {isLoggedIn ? (
                        <>
                            <Link
                                to="/profile"
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Профиль
                            </Link>
                            <button
                                onClick={handleLogout}
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Выйти
                            </button>
                        </>
                    ) : (
                        <>
                            <Link
                                to="/login"
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Войти
                            </Link>
                            <Link
                                to="/signup"
                                style={buttonStyle}
                                onMouseEnter={handleMouseEnter}
                                onMouseLeave={handleMouseLeave}
                            >
                                Зарегистрироваться
                            </Link>
                        </>
                    )}
                </div>
            </header>

            {/* Main Content - Welcome and Stats */}
            <main style={{ width: '100%', maxWidth: '1200px' }}>
                <h1 style={{ fontSize: '2.5em', marginBottom: '10px' }}>
                Добро пожаловать на нашу платформу самообразования!</h1>
                <p style={{ fontSize: '1.2em', marginBottom: '40px' }}>
                Добро пожаловать на платформу самообразования!
Откройте для себя мир знаний с нашей интерактивной платформой,
где обучение становится увлекательным и доступным. Вы можете выбирать
и изучать курсы по интересующим вас темам, проходить тестирование для
закрепления материала и отслеживать свои результаты в личном кабинете.
А если возникнут вопросы, обсудите их на странице блога с авторами и
учителями — получайте экспертные ответы и делитесь идеями в дружелюбной атмосфере!

Начните свой путь к успеху уже сегодня!</p>

                {/* Stats Cards */}
                {loading ? (
                    <p>Loading statistics...</p>
                ) : (
                    <div style={{
                        display: 'flex',
                        gap: '20px',
                        justifyContent: 'center',
                        marginTop: '30px'
                    }}>
                        <div style={{
                            background: 'white',
                            borderRadius: '10px',
                            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                            padding: '20px',
                            width: '200px',
                            textAlign: 'center'
                        }}>
                            <h3>Всего курсов</h3>
                            <p style={{ fontSize: '2em', fontWeight: 'bold', color: '#001F3F' }}>{totalCourses}</p>
                        </div>
                        <div style={{
                            background: 'white',
                            borderRadius: '10px',
                            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                            padding: '20px',
                            width: '200px',
                            textAlign: 'center'
                        }}>
                            <h3>Всего авторов</h3>
                            <p style={{ fontSize: '2em', fontWeight: 'bold', color: '#001F3F' }}>{totalAuthors}</p>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default Dashboard;
