import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect } from "react";
import { fetchDataSets } from "../../redux/slices/DataSlice";

const Datasets = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { available_datasets, error, loading, errorMessage } = useSelector(
    (state: RootState) => state.data
  );

  useEffect(() => {
    dispatch(fetchDataSets());
  }, [dispatch]);

  return <div className="text-nc-500">
    <p className="text-xl">Datasets</p>
    {loading && <p>Loading...</p>}
    {error && <p>{errorMessage}</p>}
    {available_datasets.map((dataset) => (
      <div key={dataset.id}>
        <p>{dataset.name}</p>
      </div>
    ))}

  </div>;
};

export default Datasets;
