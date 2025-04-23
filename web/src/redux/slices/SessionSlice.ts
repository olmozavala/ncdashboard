/**
 * SessionSlice.ts
 * 
 * This file implements the Redux slice for managing session state in the application.
 * It handles operations related to NetCDF data visualization sessions, including
 * listing, creating, and managing active sessions.
 */

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import { Session } from "../../models";

/**
 * SessionState interface
 * 
 * Defines the shape of the session state in the Redux store:
 * - sessions: Array of all available sessions
 * - loading: Loading state indicator
 * - error: Error state indicator
 * - activeSession: Currently selected session
 */
export interface SessionState {
  sessions: Session[];
  loading: boolean;
  error: boolean;
  activeSession: Session | null;
}

/**
 * Initial state for the session slice
 * 
 * Sets up the default values for the session state:
 * - Empty sessions array
 * - No active session
 * - Loading and error states set to false
 */
const initialState: SessionState = {
  sessions: [],
  error: false,
  loading: false,
  activeSession: null,
};

/**
 * SessionsSlice
 * 
 * Creates the Redux slice for session management with:
 * - Name: "session"
 * - Initial state
 * - Reducers for synchronous actions
 * - Extra reducers for handling async thunk actions
 */
export const SessionsSlice = createSlice({
  name: "session",
  initialState,
  reducers: {
    /**
     * setSession reducer
     * 
     * Updates the active session in the state
     * @param state - Current session state
     * @param action - Payload containing the new session
     */
    setSession: (state, action: PayloadAction<Session>) => {
      state.activeSession = action.payload;
    },
  },
  extraReducers(builder) {
    builder
      // Handle successful session listing
      .addCase(listSessions.fulfilled, (state, action) => {
        state.sessions = action.payload;
        state.loading = false;
        state.error = false;
      })
      // Handle failed session listing
      .addCase(listSessions.rejected, (state) => {
        state.sessions = [];
        state.loading = false;
        state.error = true;
      })
      // Handle pending session listing
      .addCase(listSessions.pending, (state) => {
        state.sessions = [];
        state.loading = true;
        state.error = false;
      });
  },
});

/**
 * listSessions thunk
 * 
 * Async thunk for fetching all available sessions from the backend
 * @returns Promise containing the list of sessions or an error
 */
export const listSessions = createAsyncThunk(
  "sessions/listSessions",
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(
        import.meta.env.VITE_BACKEND_API_URL + "/session/list"
      );
      const data = response.data;
      return data;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

/**
 * createSession thunk
 * 
 * Async thunk for creating a new session
 * @param datasetId - ID of the dataset to create a session for
 * @param parentid - Optional ID of the parent session
 * @returns Promise containing the created session or an error
 */
export const createSession = createAsyncThunk(
  "sessions/createSession",
  async (
    { datasetId, parentid }: { parentid?: string; datasetId: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.get(
        import.meta.env.VITE_BACKEND_API_URL + "/session/create",
        {
          params: {
            dataset_id: datasetId,
            parent_id: parentid,
          },
        }
      );
      const data = response.data;
      return data;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

// Export the setSession action creator
export const { setSession } = SessionsSlice.actions;

// Export the session reducer
export default SessionsSlice.reducer;
