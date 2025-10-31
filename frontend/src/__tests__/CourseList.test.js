import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CourseList from '../components/CourseList';

// Mock the API
jest.mock('../utils/auth', () => ({
  isAuthenticated: () => true,
  getCourses: () => Promise.resolve({ data: [{ id: 1, title: 'Test Course', description: 'Desc' }] }),
}));

test('renders course list', async () => {
  render(
    <BrowserRouter>
      <CourseList />
    </BrowserRouter>
  );
  expect(await screen.findByText('Test Course')).toBeInTheDocument();
});
