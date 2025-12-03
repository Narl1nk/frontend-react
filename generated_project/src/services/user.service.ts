import api from './api';
import { User, UserCreate, UserUpdate, UserResponse } from '../types/User.types';

export const userService = {
  async getAll(): Promise<User[]> {
    const response = await api.get<UserResponse>('/users');
    return response.data.data as User[];
  },

  async getById(id: number): Promise<User> {
    const response = await api.get<UserResponse>(`/users/${id}`);
    return response.data.data as User;
  },

  async create(data: UserCreate): Promise<User> {
    const response = await api.post<UserResponse>('/users', data);
    return response.data.data as User;
  },

  async update(id: number, data: UserUpdate): Promise<User> {
    const response = await api.patch<UserResponse>(`/users/${id}`, data);
    return response.data.data as User;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/users/${id}`);
  }
};

// Confirm export for userService object
