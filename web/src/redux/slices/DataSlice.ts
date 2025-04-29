import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import axios from "axios";
import { Dataset, DatasetInfo, datasetVariableType, Plot } from "../../models";

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
  // activeDataset: {
  //   dataset: Dataset;
  //   info: DatasetInfo;
  // } | null;
  plots: { [key: string]: Plot };
  // TODO: Remove tempImage
  // tempImage: any;
  // tempImages: { [key: string]: any };
  // tempLat: number[]; // TODO: save lat and lon with image
  // tempLon: number[]; // TODO: save lat and lon with image
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
  // activeDataset: null,
  plots: {},
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
    updateVariable: (
      state,
      action: PayloadAction<{
        dataset: string;
        variable: string;
        dataToUpdate: datasetVariableType;
      }>
    ) => {
      const datasetToUpdate = state.available_datasets.find(
        (d) => d.id === action.payload.dataset
      );

      if (datasetToUpdate) {
        const variableToUpdate =
          datasetToUpdate?.info?.variables_info[action.payload.variable];
        if (variableToUpdate) {
          variableToUpdate.checked = action.payload.dataToUpdate.checked;
          variableToUpdate.dimensions = action.payload.dataToUpdate.dimensions;
        }
      }
    },
    // setImage: (state, action: PayloadAction<any>) => {
    // state.tempImage = action.payload;
    // }

    setPlotGenerationProgess: (state, action: PayloadAction<{
      variable: string;
      progress: number;
    }>) => {
      const plot = state.plots[action.payload.variable];
      if (plot && action.payload.progress > plot.progress) {
        plot.loading = true;
        plot.progress = action.payload.progress;        
      }
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
      .addCase(
        fetchDatasetInfo.fulfilled,
        (
          state,
          action: PayloadAction<DatasetInfo, string, { arg: string }>
        ) => {
          const datasetToUpdate = state.available_datasets.find(
            (d) => d.id === action.meta.arg
          );

          /** 
          Here I am modifying the variable info to hold the state of the UI as well, for that I am using @see datasetVariableType.

          Original data structure:
          variables_info = {
            salinity: ['time', 'depth', 'lat', 'lon'],
            surf_el: ['time', 'lat', 'lon'],
            tau: ['time'],
            water_temp: ['time', 'depth', 'lat', 'lon'],
            water_u: ['time', 'depth', 'lat', 'lon'],
            water_v: ['time', 'depth', 'lat', 'lon'],
          };

          Modified data structure:
          variables_info = {
            salinity: {
              checked: true,
              dimensions: ['time', 'depth', 'lat', 'lon'],
            },

          */

          const tempInfo = action.payload;
          tempInfo.variables_info;

          for (const key in tempInfo.variables_info) {
            tempInfo.variables_info[key] = {
              checked: false,
              dimensions: tempInfo.variables_info[key] as unknown as string[],
            };
          }

          if (datasetToUpdate) {
            datasetToUpdate.info = tempInfo;
          }
          state.loading = false;
          state.error = false;
        }
      )
      .addCase(fetchDatasetInfo.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to fetch dataset info";
      })
      .addCase(getLatLon.pending, (state) => {
        state.loading = true;
        state.error = false;
        state.errorMessage = "";
      })
      .addCase(getLatLon.fulfilled, (state) => {
        state.loading = false;
        state.error = false;
      })
      .addCase(getLatLon.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to fetch lat lon";
      })
      .addCase(generatePlot.pending, (state, action) => {
        state.error = false;
        state.errorMessage = "";
        if (action.meta.arg.variable in state.plots === false) {
          state.plots[action.meta.arg.variable] = {
            dataset: action.meta.arg.dataset,
            variable: action.meta.arg.variable,
            loading: true,
            error: false,
            images: {},
            progress: 0,
          };
        } else {
          state.plots[action.meta.arg.variable].loading = true;
        }
      })
      .addCase(generatePlot.fulfilled, (state, action) => {
        state.loading = false;
        state.error = false;
        if (action.payload && action.payload.images) {
          state.plots[action.meta.arg.variable] = action.payload;
        }
      })
      .addCase(generatePlot.rejected, (state) => {
        state.error = true;
        state.loading = false;
        state.errorMessage = "Failed to generate plot";
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

async function generateImageHelper(params: {
  dataset_id: string;
  variable: string;
  time_index: number;
  depth_index: number;
}): Promise<string> {
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
    console.error("Failed to generate image:", error);
    throw error;
  }
}

export const generatePlot = createAsyncThunk(
  "data/generatePlot",
  async (
    params: {
      dataset: string;
      variable: string;
      dimension: number;
      depthIndex: number;
      timeIndex: number;
    },
    { rejectWithValue, getState}
  ) => {
    const state = getState() as { data: DataState };
    const dataset = state.data.available_datasets.find(
      (d) => d.id === params.dataset
    );
    if (dataset && dataset.info) {
      try {
        const depthCount = dataset.info.dims["depth"];
        if (params.dimension === 4) {
          if (dataset && depthCount >= params.depthIndex  ) {
            const image = await generateImageHelper({
              dataset_id: dataset.id,
              depth_index: params.depthIndex,
              variable: params.variable,
              time_index: params.timeIndex,
            });

            const key = `depth_${params.depthIndex}_time_${params.timeIndex}`;
            const existingPlot: Plot = state.data.plots[params.variable] || {
              dataset: dataset.id,
              variable: params.variable,
              loading: true,
              error: false,
              images: {},
              progress: 0,
            };

            const images = {...existingPlot.images, [key]: image};

            return {
              ...existingPlot,
              images: images,
              loading: false,
              error: false,
              progress: 100,
            }
          }
        }
      } catch (error) {
        console.error("Failed to generate plot:", error);
        return rejectWithValue("Failed to generate plot");
      }
    } else {
      rejectWithValue("Dataset not found");
    }
  }
);

// Action creators are generated for each case reducer function
export const { updateVariable ,setPlotGenerationProgess } = DataSlice.actions;
export default DataSlice.reducer;
