export const ROUTES = {
  HOME: '/',
  USER: '/userlist',
  NOT_FOUND: '*',
} as const;

export interface RouteConfig {
  path: string;
  name: string;
  protected?: boolean;
}

export const routeConfig: RouteConfig[] = [
  { path: ROUTES.HOME, name: 'Home' },
  { path: ROUTES.USER, name: 'UserList', protected: false },
  { path: ROUTES.NOT_FOUND, name: 'NotFound' }
];