/**
 * @module store
 * @description Central Redux store configuration for the application
 * 
 * This file configures the Redux store with all application slices:
 * - AuthSlice: Manages user authentication state
 * - DataSlice: Handles dataset management and visualization data
 * - ToastSlice: Controls notification system
 * - SessionsSlice: Manages data analysis sessions
 * - CanvasSlice: Handles visualization canvas state
 * 
 * The store provides:
 * - Type-safe state management
 * - Centralized state access
 * - Action dispatching capabilities
 * - Middleware integration
 * 
 * @see AuthSlice - Authentication state management
 * @see DataSlice - Dataset and visualization data
 * @see ToastSlice - Notification system
 * @see SessionsSlice - Session management
 * @see CanvasSlice - Canvas state management
 */

import { configureStore } from "@reduxjs/toolkit";
import AuthSlice from "./slices/AuthSlice";
import DataSlice from "./slices/DataSlice";
import ToastSlice from "./slices/ToastSlice";
import SessionsSlice from "./slices/SessionSlice";
import CanvasSlice from "./slices/CanvasSlice";

/**
 * Redux store configuration
 * 
 * Combines all application slices into a single store:
 * - auth: User authentication state
 * - data: Dataset and visualization data
 * - toast: Notification system
 * - session: Analysis sessions
 * - canvas: Visualization canvas
 */
export const store = configureStore({
  reducer: {
    auth: AuthSlice,
    data: DataSlice,
    toast: ToastSlice,
    session: SessionsSlice,
    canvas: CanvasSlice,
  },
});

/**
 * Type definitions for the Redux store
 * 
 * These types are automatically inferred from the store configuration:
 * - RootState: Type of the complete Redux state tree
 * - AppDispatch: Type of the dispatch function
 */
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
