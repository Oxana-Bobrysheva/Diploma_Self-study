import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import MaterialViewer from '../components/MaterialViewer';

jest.mock('../utils/auth', () => ({
  isAuthenticated: () => true,
  getMaterials: () => Promise.resolve({ data: [{ id: 1, title: 'Test Material' }] }),
  getMaterialDetails: () => Promise.resolve({ data: { title: 'Test Material', content: 'Content' } }),
}));

test('renders material viewer', async () => {
  render(
    <BrowserRouter>
      <MaterialViewer />
    </BrowserRouter>
  );
  expect(await screen.findByText('Test Material')).toBeInTheDocument();
});
