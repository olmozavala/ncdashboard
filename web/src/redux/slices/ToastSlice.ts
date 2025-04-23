/**
 * @module ToastSlice
 * @description Manages the application's toast notification system
 * 
 * This slice handles:
 * - Toast message display
 * - Toast visibility state
 * - Toast message content
 * - Toast timing and auto-dismissal
 * 
 * The slice provides:
 * - Simple toast message display
 * - Automatic dismissal after delay
 * - Message content management
 * 
 * @see store - Main Redux store configuration
 * @see components/Toast - Toast component implementation
 */

import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";

/**
 * Toast state interface
 * 
 * Defines the structure of the toast state:
 * - show: Visibility state of the toast
 * - message: The toast message content
 * - type: The type of toast (error, info, success)
 */
export interface ToastState {
  show: boolean;
  message: string;
  type: "error" | "info" | "success";
}

/**
 * Initial state for the toast slice
 * 
 * Sets up the default values for:
 * - Hidden toast
 * - Empty message
 * - Default info type
 */
const initialState: ToastState = {
  show: false,
  message: "",
  type: "info",
};

/**
 * Toast slice reducer
 * 
 * Manages state updates for:
 * - Toast message display
 * - Toast visibility
 * - Toast message content
 * - Toast type
 */
export const ToastSlice = createSlice({
  name: "toast",
  initialState,
  reducers: {
    /**
     * Shows a toast message
     * @param state - Current toast state
     * @param action - Payload containing the message to display
     */
    showToast: (state, action: PayloadAction<string>) => {
      state.message = action.payload;
      state.show = true;
    },
    /**
     * Hides the toast message
     * @param state - Current toast state
     */
    hideToast: (state) => {
      state.show = false;
    },
  },
  extraReducers(builder) {
    builder
      .addCase(openToast.fulfilled, (state) => {
        state.show = false;
      })
      .addCase(openToast.pending, (state, action) => {
        state.show = true;
        state.message = action.meta.arg.msg;
        state.type = action.meta.arg.type;
      })
      .addCase(openToast.rejected, (state) => {
        state.show = false;
        state.message = "Failed to open toast";
      });
  },
});

/**
 * Async thunk for opening a toast message
 * 
 * Handles toast display with:
 * - Message content
 * - Toast type
 * - Display duration
 */
export const openToast = createAsyncThunk(
  "data/openToast",
  async (
    ToastParam: {
      msg: string;
      type: ToastState["type"];
      time: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const { msg, type, time } = ToastParam;
      await new Promise((resolve) => {
        setTimeout(() => {
          resolve({ msg, type, time });
        }, time);
      });
      return { msg, type };
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

// Action creators are generated for each case reducer function
export const { showToast, hideToast } = ToastSlice.actions;
export default ToastSlice.reducer;
