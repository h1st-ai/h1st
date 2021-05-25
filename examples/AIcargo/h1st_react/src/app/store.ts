import { configureStore, ThunkAction, Action } from "@reduxjs/toolkit";
import uploadReducer from "features/upload_model/uploadSlice";
import executionReducer from "features/execute/executionSlice";
import appInfoReducer from "features/common/appSlice";

export const store = configureStore({
  reducer: {
    upload: uploadReducer,
    execution: executionReducer,
    app: appInfoReducer,
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
