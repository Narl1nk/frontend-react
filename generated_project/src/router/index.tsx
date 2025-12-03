import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Home, UserView, NotFound } from '../views';
import { ROUTES } from './routes';

// Ensure AppRouter is properly exported
export const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path={ROUTES.HOME} element={<Home />} />
          <Route path={ROUTES.USER} element={<UserView />} />
          <Route path={ROUTES.NOT_FOUND} element={<NotFound />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

// Add export for this file
export * from './index';

// Ensure all routing components are accessible
