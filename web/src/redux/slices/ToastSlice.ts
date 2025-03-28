import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

export interface ToastState {
  show: boolean;
  message: string;
  type: "error" | "info" | "success";
}

const initialState: ToastState = {
  show: false,
  message: "",
  type: "info",
};

export const ToastSlice = createSlice({
  name: "toast",
  initialState,
  reducers: {},
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
export const { } = ToastSlice.actions;
export default ToastSlice.reducer;
