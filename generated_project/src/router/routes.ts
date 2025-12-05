export const ROUTES = {
  HOME: '/',
  USER_FORM_VIEW: '/users/form',
  USER_LIST_VIEW: '/users/list',
  USER_MANAGEMENT_VIEW: '/users/view',
  NOT_FOUND: '*',
} as const;

export const routeConfig: RouteConfig[] = [
  { path: ROUTES.HOME, name: 'Home' },
  { path: ROUTES.USER_FORM_VIEW, name: 'UserFormView', protected: false },
  { path: ROUTES.USER_LIST_VIEW, name: 'UserListView', protected: false },
  { path: ROUTES.USER_MANAGEMENT_VIEW, name: 'UserManagementView', protected: false },
  { path: ROUTES.NOT_FOUND, name: 'NotFound' },
];