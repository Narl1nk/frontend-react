import React from 'react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../router/routes';

export const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to={ROUTES.HOME}>User Management</Link>
      </div>
      <div className="navbar-links">
        <Link to={ROUTES.USER}>Users</Link>
      </div>
    </nav>
  );
};
