/**
 * @module SelectDataset
 * @description Dataset selection interface that allows users to:
 * - Browse available datasets
 * - View dataset details on hover
 * - Navigate to dataset visualization
 * 
 * This screen serves as the entry point to the visualization system,
 * connecting the Home screen to the Dataset visualization screen.
 * 
 * @see DatasetScreen - The visualization screen that users navigate to
 * @see DataSlice - Manages dataset state and fetching
 * @see models/Dataset - Defines the dataset data structure
 */

import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { fetchDataSets } from "../../redux/slices/DataSlice";
import { Button } from "../../components";
import { useNavigate } from "react-router-dom";
import { Dataset } from "../../models";

/**
 * Dataset selection interface component
 * 
 * Implements a two-panel layout:
 * - Left panel: List of available datasets
 * - Right panel: Dataset details on hover
 * 
 * @returns {JSX.Element} Dataset selection interface with hover details
 */
const SelectDataset = () => {
  // State management
  const dispatch = useDispatch<AppDispatch>();
  const { available_datasets, error, loading, errorMessage } = useSelector(
    (state: RootState) => state.data
  );
  const navigate = useNavigate();

  // UI state
  const [hoveredDataset, setHoveredDataset] = useState<Dataset | null>(null);

  // Initial data fetch
  useEffect(() => {
    dispatch(fetchDataSets());
  }, [dispatch]);

  /**
   * Handles dataset selection and navigation
   * @param {string} datasetId - ID of the selected dataset
   */
  const onDatasetSelect = (datasetId: string) => {
    // TODO: Implement session creation
    // Check if there are sessions available
    // const dataset_sessions = sessions.filter((session) => session.dataset_id === datasetId);
    // if(sessions.length === 0 || dataset_sessions.length === 0) {
    //   dispatch(createSession({datasetId: datasetId}));
    // }
    navigate(`/${datasetId}`);
  };

  return (
    <div className="text-nc-500 p-40 flex flex-row gap-4">
      {/* Dataset list panel */}
      <div className="w-80">
        <p className="text-xl mb-4">Datasets available</p>
        {loading && <p>Loading...</p>}
        {error && <p className="text-red-500">{errorMessage}</p>}
        <div className="flex flex-col flex-wrap gap-4">
          {available_datasets &&
            available_datasets.map((dataset) => (
              <div 
                onMouseEnter={() => setHoveredDataset(dataset)} 
                key={dataset.id}
              >
                <Button
                  text={dataset.name}
                  onClick={() => onDatasetSelect(dataset.id)}
                  key={dataset.id}
                />
              </div>
            ))}
        </div>
      </div>

      {/* Dataset details panel */}
      <div className="w-full ml-40">
        <p>Dataset Info:</p>
        <p>
          {hoveredDataset === null ? (
            "Hover over a dataset to see details"
          ) : (
            <>
              <p>Name: {hoveredDataset.name}</p>
              <p>Path: {hoveredDataset.path}</p>
              <p>ID: {hoveredDataset.id}</p>
            </>
          )}
        </p>
      </div>
    </div>
  );
};

export default SelectDataset;
