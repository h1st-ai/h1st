import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { AIModel } from "features/upload_model/uploadSlice";
import { RootState, AppThunk } from "../../app/store";

export interface ExecutionState {
  model: AIModel | null;
  input?: {
    type: string;
    value: string;
  };
  output?: {
    type: string;
    result: string;
  };
}

const initialState: ExecutionState = {
  model: null,
};

export const executionSlice = createSlice({
  name: "execution",
  initialState,
  // The `reducers` field lets us define reducers and generate associated actions
  reducers: {
    // Use the PayloadAction type to declare the contents of `action.payload`
    setModel: (state, action: PayloadAction<AIModel>) => {
      state.model = action.payload;
    },
  },
});

export const { setModel } = executionSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state: RootState) => state.counter.value)`
export const selectModel = (state: RootState) => state.execution.model;

export default executionSlice.reducer;
