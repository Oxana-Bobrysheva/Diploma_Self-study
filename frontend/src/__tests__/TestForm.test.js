import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import TestForm from '../components/TestForm';

jest.mock('../utils/auth', () => ({
  isAuthenticated: () => true,
  getTests: () => Promise.resolve({ data: [{ id: 1, title: 'Test Exam' }] }),
  getTestDetails: () => Promise.resolve({ data: { title: 'Test Exam', questions: [{ id: 1, text: 'Q1?' }] } }),
}));

test('renders test form', async () => {
  render(
    <BrowserRouter>
      <TestForm />
    </BrowserRouter>
  );
  expect(await screen.findByText('Test Exam')).toBeInTheDocument();
});
