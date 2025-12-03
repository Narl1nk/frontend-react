type StorageType = 'localStorage' | 'sessionStorage';

// Base storage wrapper
function createStorage(type: StorageType) {
  const storage = type === 'localStorage' ? window.localStorage : window.sessionStorage;

  function get<T>(key: string): T | null {
    try {
      const item = storage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error(`Failed to get item from ${type}:`, error);
      return null;
    }
  }

  function set<T>(key: string, value: T): void {
    try {
      storage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Failed to set item in ${type}:`, error);
    }
  }

  function remove(key: string): void {
    try {
      storage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove item from ${type}:`, error);
    }
  }

  function clear(): void {
    try {
      storage.clear();
    } catch (error) {
      console.error(`Failed to clear ${type}:`, error);
    }
  }

  function has(key: string): boolean {
    return get(key) !== null;
  }

  return { get, set, remove, clear, has };
}

const localStorageUtil = createStorage('localStorage');
const sessionStorageUtil = createStorage('sessionStorage');

// Token handling logic
export const tokenStorage = {
  setAuthToken(token: string): void {
    localStorageUtil.set('authToken', token);
  },
  getAuthToken(): string | null {
    return localStorageUtil.get<string>('authToken');
  },
  removeAuthToken(): void {
    localStorageUtil.remove('authToken');
  }
};

export const storageUtil = { localStorageUtil, sessionStorageUtil };
