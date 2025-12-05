// Type-safe storage utility for localStorage with generic methods
export const storage = {
  get<T>(key: string): T | null {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) as T : null;
    } catch (error) {
      console.error(`Error getting ${key} from localStorage`, error);
      return null;
    }
  },

  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error setting ${key} to localStorage`, error);
    }
  },

  remove(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing ${key} from localStorage`, error);
    }
  },

  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage', error);
    }
  },

  has(key: string): boolean {
    return localStorage.getItem(key) !== null;
  }
};

// Type-safe storage utility for sessionStorage with generic methods
export const sessionStorage = {
  get<T>(key: string): T | null {
    try {
      const value = sessionStorage.getItem(key);
      return value ? JSON.parse(value) as T : null;
    } catch (error) {
      console.error(`Error getting ${key} from sessionStorage`, error);
      return null;
    }
  },

  set<T>(key: string, value: T): void {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error setting ${key} to sessionStorage`, error);
    }
  },

  remove(key: string): void {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing ${key} from sessionStorage`, error);
    }
  },

  clear(): void {
    try {
      sessionStorage.clear();
    } catch (error) {
      console.error('Error clearing sessionStorage', error);
    }
  },

  has(key: string): boolean {
    return sessionStorage.getItem(key) !== null;
  }
};

// Token management helpers
export const tokenStorage = {
  setAuthToken(token: string): void {
    storage.set('authToken', token);
  },

  getAuthToken(): string | null {
    return storage.get<string>('authToken');
  },

  removeAuthToken(): void {
    storage.remove('authToken');
  }
};