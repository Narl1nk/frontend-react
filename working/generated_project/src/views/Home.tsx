import React from 'react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../router/routes';

export const Home: React.FC = () => {
  return (
    <div className="home-view">
      <h1>Welcome to User Management System</h1>
      <div className="quick-links">
        <Link to={ROUTES.USER}>Manage Users</Link>
      </div>
    </div>
  );
};