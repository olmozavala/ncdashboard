/**
 * @module DatasetScreen
 * @description Interactive dataset visualization interface for exploring and analyzing scientific data
 *
 * This screen is the core visualization component of the application, providing an interface for:
 * - Selecting and analyzing dataset variables
 * - Navigating through depth levels of data
 * - Visualizing data on an interactive map
 * - Managing data sessions and caching
 *
 * System Architecture:
 * 1. Data Management:
 *    - Uses Redux DataSlice to manage dataset state
 *    - Fetches and caches dataset information and images
 *    - Maintains latitude/longitude data for map visualization
 *
 * 2. Visualization:
 *    - Uses OpenLayers Map component for data display
 *    - Supports multiple depth levels of data
 *    - Provides real-time updates as parameters change
 *
 * 3. State Management:
 *    - Redux for global state (datasets, images, sessions)
 *    - Local state for UI controls (variables, depth index)
 *    - Automatic state synchronization between components
 *
 * 4. Data Flow:
 *    - User selects variable → Generates images for all depths
 *    - User changes depth → Updates map visualization
 *    - Data is cached to improve performance
 *
 * @dependencies
 * - Redux: State management
 * - React Router: Navigation
 * - react-resizable-panels: Layout management
 * - OpenLayers: Map visualization
 * - Axios: API communication
 */

import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect } from "react";

import {
  fetchDatasetInfo,
  fetchDataSets,
  updateVariable,
} from "../../redux/slices/DataSlice";
import { Button, CheckBox, FourDPlot, ThreeDPlot, OneDPlot } from "../../components";

/**
 * Dataset visualization interface component
 *
 * The component implements a split-panel layout:
 * - Left Panel: Control interface for variable selection and depth navigation
 * - Right Panel: Interactive map visualization of selected data
 *
 * @returns {JSX.Element} Split-panel layout with variable controls and map visualization
 */
const DatasetScreen = () => {
  // State management
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { datasetId } = useParams();

  // Redux state selectors
  const { available_datasets, loading } = useSelector(
    (state: RootState) => state.data
  );

  const selectedDataset = available_datasets.find(
    (dataset) => dataset.id === datasetId
  );


  const variables = Object.keys(selectedDataset?.info?.variables_info || {});

  /**
   * Handles variable selection with single-select behavior
   * @param {string} v - Selected variable
   */
  const onVariableSelect = (v: string) => {

    if (selectedDataset && selectedDataset.info && datasetId) {
      dispatch(
        updateVariable({
          dataset: datasetId,
          variable: v,
          dataToUpdate: {
            checked: !selectedDataset.info.variables_info[v].checked,
            dimensions: selectedDataset.info.variables_info[v].dimensions,
          },
        })
      );
    }
  };

  // Data fetching effects
  useEffect(() => {
    if (available_datasets.length === 0) {
      dispatch(fetchDataSets());
    }
  }, [dispatch]);

  useEffect(() => {
    if (selectedDataset && !selectedDataset.info) {
      dispatch(fetchDatasetInfo(selectedDataset.id));
    }
  }, [selectedDataset]);


  // Render
  return (
    <div className="text-nc-500 p-4 w-full">
      {/* Dataset not found state */}
      {!selectedDataset && (
        <>
          <p className="text-xl mb-4">Dataset not found</p>
          <Button
            text="View available datasets"
            onClick={() => navigate("/datasets")}
          />
        </>
      )}

      {/* Loading state */}
      {loading ? (
        <h1 className="text-2xl">Loading...</h1>
      ) : (
        <h1 className="text-2xl">{selectedDataset?.name}</h1>
      )}

      {/* Control panel */}
      <div>
        {/* Variable selection */}
        {variables &&
          variables.map((v) => (
            <CheckBox
              key={v}
              label={`${v} [${selectedDataset?.info?.variables_info[v].dimensions.length}D]`}
              id={v}
              checked={selectedDataset?.info?.variables_info[v].checked}
              onChange={() => onVariableSelect(v)}
            />
          ))}
        <br />
      </div>
      
      <div className="grid grid-cols-3 gap-4">
      {datasetId && variables
        ? variables.map((v) => {
            if (selectedDataset?.info?.variables_info[v].checked && selectedDataset?.info?.variables_info[v].dimensions.length === 4) {
              return <FourDPlot variable={v} dataset={datasetId} key={v} height={500} width={500} />;
            }
            if (selectedDataset?.info?.variables_info[v].checked && selectedDataset?.info?.variables_info[v].dimensions.length === 3) {
              return <ThreeDPlot variable={v} dataset={datasetId} key={v} height={500} width={500} />;
            }
            if (selectedDataset?.info?.variables_info[v].checked && selectedDataset?.info?.variables_info[v].dimensions.length === 1) {
              return <OneDPlot variable={v} dataset={datasetId} key={v} height={500} width={500} />;
            }
          })
        : null}
      </div>
    </div>
  );
};

export default DatasetScreen;
