/**
 * @module AuthSlice
 * @description Manages the application's authentication state
 * 
 * This slice handles:
 * - User authentication status
 * - User session management
 * - Authentication token storage
 * - User permissions
 * 
 * The slice provides:
 * - Authentication state tracking
 * - User session persistence
 * - Permission management
 * 
 * @see store - Main Redux store configuration
 * @see components/Auth - Authentication components
 */

import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/**
 * Authentication state interface
 * 
 * Defines the structure of the authentication state:
 * - isAuthenticated: User authentication status
 * - user: User information (id, username, email)
 * - token: Authentication token
 * - permissions: User permissions list
 */
interface AuthState {
  isAuthenticated: boolean;
  user: {
    id: string;
    username: string;
    email: string;
  } | null;
  token: string | null;
  permissions: string[];
}

/**
 * Initial state for the auth slice
 * 
 * Sets up the default values for:
 * - Not authenticated
 * - No user information
 * - No authentication token
 * - Empty permissions list
 */
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  permissions: [],
};

/**
 * Authentication slice reducer
 * 
 * Manages state updates for:
 * - Authentication status
 * - User information
 * - Session tokens
 * - User permissions
 */
export const AuthSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    /**
     * Sets authentication status
     * @param state - Current auth state
     * @param action - Payload containing auth status
     */
    setAuthStatus: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload;
    },
    /**
     * Sets user information
     * @param state - Current auth state
     * @param action - Payload containing user data
     */
    setUser: (state, action: PayloadAction<AuthState["user"]>) => {
      state.user = action.payload;
    },
    /**
     * Sets authentication token
     * @param state - Current auth state
     * @param action - Payload containing token
     */
    setToken: (state, action: PayloadAction<string | null>) => {
      state.token = action.payload;
    },
    /**
     * Sets user permissions
     * @param state - Current auth state
     * @param action - Payload containing permissions
     */
    setPermissions: (state, action: PayloadAction<string[]>) => {
      state.permissions = action.payload;
    },
  },
});

export const { setAuthStatus, setUser, setToken, setPermissions } = AuthSlice.actions;
export default AuthSlice.reducer;