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
import { useEffect, useState } from "react";

import {
  fetchDatasetInfo,
  fetchDataSets,
  generateImage,
  setImage,
  getLatLon,
} from "../../redux/slices/DataSlice";
import { Button, CheckBox } from "../../components";
import { listSessions } from "../../redux/slices/SessionSlice";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { datasetVariableType } from "../../models";
import Map from "../../components/Map/Map";
import { openToast } from "../../redux/slices/ToastSlice";

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
  const {
    available_datasets,
    loading,
    activeDataset,
    tempImages,
    tempImage,
    tempLat,
    tempLon,
  } = useSelector((state: RootState) => state.data);
  const { sessions } = useSelector((state: RootState) => state.session);

  // Local state
  const [variables, setVariables] = useState<datasetVariableType>([]);
  const [depthIndex, setDepthIndex] = useState(0);

  // Derived state
  const selectedDataset = available_datasets.find(
    (dataset) => dataset.id === datasetId
  );

  /**
   * Generates visualizations for all depth levels of selected variable
   * 
   * Process:
   * 1. Validates variable selection
   * 2. Fetches latitude/longitude data for map positioning
   * 3. Generates images for each depth level
   * 4. Caches generated images for performance
   * 
   * @async
   */
  const plotAll = async () => {
    const datasetName = selectedDataset?.name;
    const variableName = variables.find((v) => v.checked)?.variable;
    const depthCount = activeDataset?.info.dims["depth"];

    if (!variableName) {
      dispatch(openToast({
        msg: "Please select a variable",
        type: "info",
        time: 2000
      }));
      return;
    }

    if (datasetId) {
      dispatch(getLatLon({ dataset: datasetId }));
    }

    if (depthCount && datasetName && variableName) {
      for (let i = 0; i < depthCount; i++) {
        if (!tempImages.hasOwnProperty(variableName + i)) {
          dispatch(
            generateImage({
              dataset: datasetName,
              variable: variableName,
              depth_index: i,
              time_index: 0, // TODO: Add time index selection
            })
          );
        }
      }
    }
  };

  /**
   * Updates visualization when depth level changes
   * 
   * Process:
   * 1. Checks if image exists in cache
   * 2. Updates map visualization with new depth data
   */
  const handleDepthChange = () => {
    const datasetName = selectedDataset?.name;
    const variableName = variables.find((v) => v.checked)?.variable;
    
    if (variableName && datasetName && tempImages.hasOwnProperty(variableName + depthIndex)) {
      dispatch(setImage(tempImages[variableName + depthIndex]));
    }
  };

  /**
   * Handles variable selection with single-select behavior
   * @param {datasetVariableType[0]} v - Selected variable
   */
  const onVariableSelect = (v: datasetVariableType[0]) => {
    setVariables(prev => prev.map(temp_v => ({
      ...temp_v,
      checked: temp_v.variable === v.variable
    })));
  };

  // Data fetching effects
  useEffect(() => {
    if (available_datasets.length === 0) {
      dispatch(fetchDataSets());
    }
  }, [dispatch]);

  useEffect(() => {
    if (sessions.length === 0) {
      dispatch(listSessions());
    }
    if (selectedDataset) {
      dispatch(fetchDatasetInfo(selectedDataset.id));
    }
  }, [selectedDataset]);

  // State synchronization effects
  useEffect(() => {
    if (activeDataset) {
      setVariables(
        Object.entries(activeDataset.info.variables_info).map(
          ([key, value]) => ({
            variable: key,
            checked: false,
            dimensions: value,
          })
        )
      );
    }
  }, [activeDataset]);

  useEffect(() => {
    handleDepthChange();
  }, [depthIndex]);

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

      {/* Main content */}
      <PanelGroup direction="horizontal" className="mt-4">
        {/* Control panel */}
        <Panel defaultSize={50}>
          <div style={{ height: "80vh" }}>
            {/* Variable selection */}
            {variables.map((v) => (
              <CheckBox
                key={v.variable}
                label={`${v.variable} [${v.dimensions.length}D]`}
                id={v.variable}
                checked={v.checked}
                onChange={() => onVariableSelect(v)}
              />
            ))}

            <br />

            {/* Plot controls */}
            <Button loading={loading} onClick={plotAll} text="Plot" />
            <br />

            {/* Depth navigation */}
            <label>Depth index: {depthIndex}</label>
            <input
              style={{ width: "100%" }}
              type="range"
              disabled={loading}
              min="0"
              max={activeDataset?.info.dims["depth"]}
              value={depthIndex}
              onChange={(e) => setDepthIndex(parseInt(e.target.value))}
            />
          </div>
        </Panel>

        {/* Visualization panel */}
        <PanelResizeHandle className="border" />
        <Panel defaultSize={50} maxSize={80}>
          <div style={{ zIndex: 90, width: "100%", height: "100%" }}>
            {tempLat.length > 0 && tempLon.length > 0 && (
              <Map
                image={tempImage}
                lat={[tempLat[0], tempLat[tempLat.length - 1]]}
                lon={[tempLon[0], tempLon[tempLon.length - 1]]}
              />
            )}
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
};

export default DatasetScreen;
