import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { fetchDataSets } from "../../redux/slices/DataSlice";
import { Button } from "../../components";
import { useNavigate } from "react-router-dom";
import { Dataset } from "../../models";

const SelectDataset = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { available_datasets, error, loading, errorMessage } = useSelector(
    (state: RootState) => state.data
  );
  const navigate = useNavigate();

  const [hoveredDataset, setHoveredDataset] = useState<Dataset | null>(null);

  useEffect(() => {
    dispatch(fetchDataSets());
  }, [dispatch]);

  const onDatasetSelect = (datasetId: string) => {
    // Check if there are sessions available
    // const dataset_sessions = sessions.filter((session) => session.dataset_id === datasetId);
    // if(sessions.length === 0 || dataset_sessions.length === 0) {
    //   dispatch(createSession({datasetId: datasetId}));
    // }
    navigate(`/${datasetId}`);
  };

  return (
    <div className="text-nc-500 p-40 flex flex-row gap-4">
      <div className="w-80">
        <p className="text-xl mb-4">Datasets available</p>
        {loading && <p>Loading...</p>}
        {error && <p className="text-red-500">{errorMessage}</p>}
        <div className="flex flex-col flex-wrap gap-4">
          {available_datasets &&
            available_datasets.map((dataset) => (
              <div onMouseEnter={() => setHoveredDataset(dataset)} key={dataset.id}>
                <Button
                  text={dataset.name}
                  onClick={() => onDatasetSelect(dataset.id)}
                  key={dataset.id}
                />
              </div>
            ))}
        </div>
      </div>
      <div className="w-full ml-40 ">
        <p>Dataset Info:</p>
        <p>{hoveredDataset === null? "Hover over a dataset to see details" : <>
          <p>Name : {hoveredDataset.name}</p>
          <p>Path : {hoveredDataset.path}</p>
          <p>ID: {hoveredDataset.id}</p>
        </> }</p>
      </div>
    </div>
  );
};

export default SelectDataset;
