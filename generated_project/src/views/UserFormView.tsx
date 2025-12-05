import React, { useState } from 'react';
import { UserForm } from '../components';

export const UserFormView: React.FC = () => {
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="user-form-view">
      <h1>{showForm ? 'Edit User' : 'Add User'}</h1>
      <button onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Cancel' : 'Create New User'}
      </button>
      {showForm && (
        <UserForm onSubmit={() => setShowForm(false)} />
      )}
    </div>
  );
};
