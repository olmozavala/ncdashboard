import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect } from "react";
import { fetchDataSets } from "../../redux/slices/DataSlice";
import { Button } from "../../components";
import { createSession, listSessions } from "../../redux/slices/SessionSlice";

const DatasetScreen = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { datasetId } = useParams();
  const { available_datasets, loading } = useSelector(
    (state: RootState) => state.data
  );
  const { sessions } = useSelector((state: RootState) => state.session);

  const selectedDataset = available_datasets.find(
    (dataset) => dataset.id === datasetId
  );

  let dataset_sessions = sessions.filter(
    (session) => session.dataset_id === datasetId
  );

  useEffect(() => {
    if (available_datasets.length === 0) {
      dispatch(fetchDataSets());
    }
  }, [dispatch]);

  useEffect(() => {
    if (sessions.length === 0) {
      dispatch(listSessions()).then(() => {
        dataset_sessions = sessions.filter(
          (session) => session.dataset_id === datasetId
        );
      });
    }
  }, [selectedDataset]);

  return (
    <div className="text-nc-500 p-4">
      {!selectedDataset ? (
        <>
          <p className="text-xl mb-4">Dataset not found</p>
          <Button
            text="View available datasets"
            onClick={() => navigate("/datasets")}
          />
        </>
      ) : null}
      <h1>{loading ? "Loading..." : selectedDataset?.name}</h1>


    </div>
  );
};

export default DatasetScreen;
