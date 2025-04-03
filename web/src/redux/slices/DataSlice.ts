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
  // TODO: Remove tempImage
  tempImage: any;
  tempImages: { [key: string]: any };
  tempLat: number[]; // TODO: save lat and lon with image
  tempLon: number[]; // TODO: save lat and lon with image
}

const initialState: DataState = {
  available_datasets: [],
  error: false,
  loading: false,
  errorMessage: "",
  activeDataset: null,
  tempImages: {},
  tempImage: null,
  tempLat: [],
  tempLon: [],
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
    setImage: (state, action: PayloadAction<any>) => {
      state.tempImage = action.payload;
    }
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
      .addCase(
        fetchDatasetInfo.fulfilled,
        (
          state,
          action: PayloadAction<DatasetInfo, string, { arg: string }>
        ) => {
          state.activeDataset = {
            dataset: state.available_datasets.find(
              (d) => d.id === action.meta.arg
            ) as Dataset,
            info: action.payload,
          };
          state.loading = false;
          state.error = false;
        }
      )
      .addCase(fetchDatasetInfo.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to fetch dataset info";
      })
      .addCase(generateImage.pending, (state) => {
        state.loading = true;
        state.error = false;
        state.errorMessage = "";
      })
      .addCase(generateImage.fulfilled, (state, action) => {
        state.loading = false;
        state.error = false;
        state.tempImages = {
          ...state.tempImages,
          [action.meta.arg.variable + action.meta.arg.depth_index]: action.payload}
      })
      .addCase(generateImage.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to generate image";
      })
      .addCase(getLatLon.pending, (state) => {
        state.loading = true;
        state.error = false;
        state.errorMessage = "";
      })
      .addCase(getLatLon.fulfilled, (state, action) => {
        state.tempLat = action.payload.lat;
        state.tempLon = action.payload.lon;
        state.loading = false;
        state.error = false;
      })
      .addCase(getLatLon.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to fetch lat lon";
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

export const generateImage = createAsyncThunk(
  "data/generateImage",
  async (
    params: {
      dataset: string;
      variable: string;
      time_index: number;
      depth_index: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.post(
        import.meta.env.VITE_BACKEND_API_URL + `/image/generate`,
        params,
        {
          responseType: "blob",
        }
      );
      const data = response.data;

      const blob = new Blob([data], { type: "image/png" });
      const url = URL.createObjectURL(blob);

      return url;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);

export const getLatLon = createAsyncThunk(
  "data/getLatLon",
  async (
    params: {
      dataset: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await axios.get(
        import.meta.env.VITE_BACKEND_API_URL + `/data/info/lat_lon`,
        {
          params: {
            dataset_id: params.dataset,
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
export const { setActiveDataset, setImage } = DataSlice.actions;
export default DataSlice.reducer;
