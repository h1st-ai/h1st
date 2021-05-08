import { configureStore, ThunkAction, Action } from "@reduxjs/toolkit";
import counterReducer from "../features/counter/counterSlice";
import uploadReducer from "../features/upload_model/uploadSlice";
import executionReducer from "../features/execute/executionSlice";

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    upload: uploadReducer,
    execution: executionReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
