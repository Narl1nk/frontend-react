export interface User {
  id: number;
  email: string;
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
