import React from 'react';
import { UserList } from '../components';

export const UserListView: React.FC = () => {
  return (
    <div className="user-list-view">
      <h1>User Management</h1>
      <UserList />
    </div>
  );
};
