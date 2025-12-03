export interface User {
  id: number; // primary key, auto increment
  email: string; // unique constraint, max length: 255
  createdAt: string; // required
  updatedAt: string; // required
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