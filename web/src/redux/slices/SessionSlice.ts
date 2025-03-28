import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import { Session } from "../../models";

export interface SessionState {
  sessions: Session[];
  loading: boolean;
  error: boolean;
  activeSession: Session | null;
}

const initialState: SessionState = {
  sessions: [],
  error: false,
  loading: false,
  activeSession: null,
};

export const SessionsSlice = createSlice({
  name: "session",
  initialState,
  reducers: {
    setSession: (state, action: PayloadAction<Session>) => {
      state.activeSession = action.payload;
    },
  },
  extraReducers(builder) {
    builder
      .addCase(listSessions.fulfilled, (state, action) => {
        state.sessions = action.payload;
        state.loading = false;
        state.error = false;
      })
      .addCase(listSessions.rejected, (state) => {
        state.sessions = [];
        state.loading = false;
        state.error = true;
      })
      .addCase(listSessions.pending, (state) => {
        state.sessions = [];
        state.loading = true;
        state.error = false;
      });
  },
});

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

// Action creators are generated for each case reducer function
export const { setSession } = SessionsSlice.actions;
export default SessionsSlice.reducer;
