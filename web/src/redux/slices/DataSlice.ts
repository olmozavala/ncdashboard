import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import { Dataset, DatasetInfo } from "../../models";

/**
 * @module DataSlice
 * @description Manages the application's dataset and visualization data state
 * 
 * This slice handles:
 * - Dataset fetching and management
 * - Visualization data processing
 * - Error handling and loading states
 * - Data transformation and normalization
 * 
 * The slice maintains:
 * - Available datasets list
 * - Current dataset details
 * - Visualization data
 * - Loading and error states
 * 
 * @see store - Main Redux store configuration
 * @see models/Dataset - Dataset data structure
 * @see models/DatasetInfo - Dataset information structure
 */

/**
 * Data state interface
 * 
 * Defines the structure of the data state:
 * - available_datasets: List of all available datasets
 * - loading: Loading state indicator
 * - error: Error state indicator
 * - errorMessage: Error message content
 * - activeDataset: Currently selected dataset and its info
 * - tempImage: Temporary image storage
 * - tempImages: Map of temporary images by key
 * - tempLat: Temporary latitude data
 * - tempLon: Temporary longitude data
 */
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

/**
 * Initial state for the data slice
 * 
 * Sets up the default values for:
 * - Empty dataset list
 * - No active dataset
 * - No loading or errors
 * - Empty temporary storage
 */
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

/**
 * Data slice reducer
 * 
 * Manages state updates for:
 * - Dataset fetching
 * - Visualization data processing
 * - Error handling
 * - Loading states
 * - Temporary data storage
 */
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

/**
 * Async thunk for fetching available datasets
 * 
 * Makes an API call to retrieve the list of available datasets
 * Updates the state with the fetched data or error information
 */
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

/**
 * Async thunk for fetching dataset information
 * 
 * Retrieves detailed information about a specific dataset
 * Updates the active dataset state with the fetched info
 */
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

/**
 * Async thunk for generating visualization images
 * 
 * Creates visualization images based on dataset parameters:
 * - Variable selection
 * - Time index
 * - Depth index
 */
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

/**
 * Async thunk for retrieving latitude and longitude data
 * 
 * Fetches geographical coordinates for a specific dataset
 * Used for spatial visualization and mapping
 */
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
