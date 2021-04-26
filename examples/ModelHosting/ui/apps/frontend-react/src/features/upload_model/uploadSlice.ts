import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState, AppThunk } from "../../app/store";
import { fetchCount } from "./counterAPI";

export interface UploadState {
  showUploadForm: boolean;
  status: "idle" | "loading" | "failed";
  models: AIModel[];
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  creator: string;
}

const initialState: UploadState = {
  showUploadForm: false,
  status: "idle",
  models: [],
};

export const uploadSlice = createSlice({
  name: "upload",
  initialState,
  // The `reducers` field lets us define reducers and generate associated actions
  reducers: {
    toggleUploadState: (state) => {
      // Redux Toolkit allows us to write "mutating" logic in reducers. It
      // doesn't actually mutate the state because it uses the Immer library,
      // which detects changes to a "draft state" and produces a brand new
      // immutable state based off those changes
      state.showUploadForm = !state.showUploadForm;
    },
    setStatus: (
      state,
      action: PayloadAction<"idle" | "loading" | "failed">
    ) => {
      state.status = action.payload;
    },
    // Use the PayloadAction type to declare the contents of `action.payload`
    setModels: (state, action: PayloadAction<AIModel[]>) => {
      state.models = action.payload;
    },
    addModel: (state, action: PayloadAction<AIModel>) => {
      state.models.unshift(action.payload);
    },
  },
});

export const {
  toggleUploadState,
  setStatus,
  setModels,
  addModel,
} = uploadSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state: RootState) => state.counter.value)`
export const selectShowModalState = (state: RootState) =>
  state.upload.showUploadForm;

export default uploadSlice.reducer;
