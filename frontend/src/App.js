import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Dashboard from './components/Dashboard';
import CourseList from './components/CourseList';
import CourseDetail from './components/CourseDetail';
import MaterialViewer from './components/MaterialViewer';
import TestForm from './components/TestForm';
import Profile from './components/Profile';
import TeachersList from './components/TeachersList';
import AddMaterial from './components/AddMaterial';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/teachers" element={<TeachersList />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/courses" element={<CourseList />} />
          <Route path="/courses/:id" element={<CourseDetail />} />
          <Route path="/courses/:courseId/materials" element={<MaterialViewer />} />
          <Route path="/courses/:id/add-material" element={<AddMaterial />} />
          <Route path="/courses/:courseId/tests" element={<TestForm />} />
          <Route path="/" element={<Dashboard />} />  {/* Ensure this is set to Dashboard */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
