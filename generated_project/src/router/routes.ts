export const ROUTES = {
  HOME: '/',
  USER: '/user',
  NOT_FOUND: '*',
};

export interface RouteConfig {
  path: string;
  name: string;
  protected?: boolean;
}

export const routeConfig: RouteConfig[] = [
  { path: ROUTES.HOME, name: 'Home' },
  { path: ROUTES.USER, name: 'User', protected: false },
];