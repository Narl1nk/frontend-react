export interface User {
  id: number; // primary key, auto increment
  email: string; // required, unique, max length: 255
  createdAt: string;
  updatedAt: string;
}

export interface UserCreate {
  email: string;
}

export interface UserUpdate {
  id: number;
  email?: string;
}

export interface UserResponse {
  success: boolean;
  data: User | User[];
  message?: string;
}