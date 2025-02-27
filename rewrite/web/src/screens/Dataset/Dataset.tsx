import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { fetchDatasetInfo, fetchDataSets } from "../../redux/slices/DataSlice";
import { Button, CheckBox } from "../../components";
import { createSession, listSessions } from "../../redux/slices/SessionSlice";
import { Panel, PanelGroup } from "react-resizable-panels";

const DatasetScreen = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { datasetId } = useParams();
  const { available_datasets, loading, activeDataset, error, errorMessage } =
    useSelector((state: RootState) => state.data);
  const { sessions } = useSelector((state: RootState) => state.session);

  const [variables, setVariables] = useState<
    {
      variable: string;
      checked: boolean;
      dimensions: string[];
    }[]
  >([]);

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

    if (selectedDataset) {
      dispatch(fetchDatasetInfo(selectedDataset.id));
    }
  }, [selectedDataset]);

  useEffect(() => {
    if (activeDataset !== null) {
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

  const handleVariableClick = (variable: string) => {
    setVariables(
      variables.map((v) =>
        v.variable === variable ? { ...v, checked: !v.checked } : v
      )
    );
  };

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
      {loading ? (
        "Loading..."
      ) : (
        <h1 className="text-2xl">{selectedDataset?.name}</h1>
      )}

      <PanelGroup direction="horizontal">
        <Panel>
          <div className="flex flex-col gap-4 mt-8">
            {activeDataset && (
              <>
                <h3 className="text-lg">Variables</h3>
                <div className="flex flex-col gap-2">
                  {variables.map((v, i) => (
                    <div key={i}>
                      <CheckBox
                        label={v.variable}
                        checked={v.checked}
                        onChange={() => handleVariableClick(v.variable)}
                      />
                      <p className="text-sm text-nc-400 pl-6">Dims: {v.dimensions.join(",")}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
};

export default DatasetScreen;
