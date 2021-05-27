import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState, AppThunk } from "../../app/store";

export interface AppInfoState {
  dialog: {
    type: DialogType;
    action: ActionType;
    title: string;
    message: string;
  } | null;
}

export enum ActionType {
  YESNO = "YESNO",
  OK = "OK",
}

export enum DialogType {
  ERROR = "ERROR",
  INFO = "INFO",
}

const initialState: AppInfoState = {
  dialog: null,
};

export interface SetDialogPayload {
  type: DialogType;
  action: ActionType;
  title: string;
  message: string;
}

export const uploadSlice = createSlice({
  name: "info",
  initialState,
  // The `reducers` field lets us define reducers and generate associated actions
  reducers: {
    setGlobalDialogMessage: (
      state,
      action: PayloadAction<SetDialogPayload | null>
    ) => {
      state.dialog = action.payload;
    },
  },
});

export const { setGlobalDialogMessage } = uploadSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state: RootState) => state.counter.value)`
export const selectGlobalMessage = (state: RootState) => state.app.dialog;

export default uploadSlice.reducer;
