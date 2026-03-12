export type AuthUser = {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
};

export type AuthResponse = {
  user: AuthUser;
  access_token: string;
  token_type: 'bearer';
};

export type AuthSession = {
  user: AuthUser;
  accessToken: string;
  tokenType: 'bearer';
};
