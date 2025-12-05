import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Home, UserFormView, UserListView, UserView, NotFound } from '../views';
import { ROUTES } from './routes';

export const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path={ROUTES.HOME} element={<Home />} />
          <Route path={ROUTES.USER_FORM_VIEW} element={<UserFormView />} />
          <Route path={ROUTES.USER_LIST_VIEW} element={<UserListView />} />
          <Route path={ROUTES.USER_MANAGEMENT_VIEW} element={<UserView />} />
          <Route path={ROUTES.NOT_FOUND} element={<NotFound />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};