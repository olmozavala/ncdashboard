import { configureStore } from "@reduxjs/toolkit";
import AuthSlice from "./slices/AuthSlice";
import DataSlice from "./slices/DataSlice";
import ToastSlice from "./slices/ToastSlice";
import SessionsSlice  from "./slices/SessionSlice";

export const store = configureStore({
  reducer: {
    auth: AuthSlice,
    data: DataSlice,
    toast: ToastSlice,
    session: SessionsSlice
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;