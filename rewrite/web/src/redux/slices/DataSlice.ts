import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import { Dataset, DatasetInfo } from "../../models";

export interface DataState {
  available_datasets: Dataset[];
  loading: boolean;
  error: boolean;
  errorMessage: string;
  activeDataset: {
    dataset: Dataset;
    info: DatasetInfo;
  } | null;
}

const initialState: DataState = {
  available_datasets: [],
  error: false,
  loading: false,
  errorMessage: "",
  activeDataset: null,
};

export const DataSlice = createSlice({
  name: "data",
  initialState,
  reducers: {
    setActiveDataset: (
      state,
      action: PayloadAction<DataState["activeDataset"]>
    ) => {
      state.activeDataset = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDataSets.fulfilled, (state, action) => {
        state.available_datasets = action.payload;
        state.loading = false;
      })
      .addCase(fetchDataSets.rejected, (state) => {
        state.error = true;
        state.loading = false;
        // TODO: Remove hardcoded error message
        state.errorMessage = "Failed to fetch data sets";
      })
      .addCase(fetchDataSets.pending, (state) => {
        state.loading = true;
        state.error = false;
        state.errorMessage = "";
      })
      .addCase(fetchDatasetInfo.pending, (state) => {
        state.loading = true;
        state.error = false;
        state.errorMessage = "";
      })
      .addCase(fetchDatasetInfo.fulfilled, (state, action:PayloadAction<DatasetInfo,string,{arg:string}>) => {
        state.activeDataset = {
          dataset: (state.available_datasets.find(d => d.id === action.meta.arg) as Dataset),
          info: action.payload,
        };
        state.loading = false;
        state.error = false;
      })
      .addCase(fetchDatasetInfo.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to fetch dataset info";
      });
  },
});

export const fetchDataSets = createAsyncThunk(
  "data/fetchDataSets",
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(
        import.meta.env.VITE_BACKEND_API_URL + "/data/list"
      );
      const data = response.data.datasets;
      return data;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const fetchDatasetInfo = createAsyncThunk(
  "data/fetchDatasetInfo",
  async (datasetId: string, { rejectWithValue }) => {
    try {
      const response = await axios.get(
        import.meta.env.VITE_BACKEND_API_URL + `/data/info`,
        {
          params: {
            dataset_id: datasetId,
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
export const { setActiveDataset } = DataSlice.actions;
export default DataSlice.reducer;
