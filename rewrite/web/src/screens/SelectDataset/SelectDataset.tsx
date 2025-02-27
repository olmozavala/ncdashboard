import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect } from "react";
import { fetchDataSets } from "../../redux/slices/DataSlice";
import { Button } from "../../components";
import { useNavigate } from "react-router-dom";

const SelectDataset = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { available_datasets, error, loading, errorMessage } = useSelector(
    (state: RootState) => state.data
  );

  const navigate = useNavigate();

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
    <div className="text-nc-500 p-40">
      <p className="text-xl mb-4">Datasets available</p>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{errorMessage}</p>}
      <div className="flex flex-col flex-wrap gap-4">
        {available_datasets &&
          available_datasets.map((dataset) => (
            <Button
              text={dataset.name}
              onClick={() => onDatasetSelect(dataset.id)}
              key={dataset.id}
            />
          ))}
      </div>
    </div>
  );
};

export default SelectDataset;
