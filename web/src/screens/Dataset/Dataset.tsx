import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { AppDispatch, RootState } from "../../redux/store";
import { OlHTMLAttributes, useEffect, useRef, useState } from "react";

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

const DatasetScreen = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { datasetId } = useParams();
  const {
    available_datasets,
    loading,
    activeDataset,
    error,
    errorMessage,
    tempImages,
    tempImage,
    tempLat,
    tempLon,
  } = useSelector((state: RootState) => state.data);
  const { sessions } = useSelector((state: RootState) => state.session);

  const [variables, setVariables] = useState<datasetVariableType>([]);
  const [depthIndex, setDepthIndex] = useState(0);
  // const [mapDimensions, setMapDimensions] = useState({ width: 0, height: 0 });

  // const imageRef = useRef<HTMLImageElement>(null);

  const selectedDataset = available_datasets.find(
    (dataset) => dataset.id === datasetId
  );

  let dataset_sessions = sessions.filter(
    (session) => session.dataset_id === datasetId
  );

  const handlePlotClick = () => {
    const datasetName = selectedDataset?.name;
    const variableName = variables.find((v) => v.checked)?.variable;
    if (variableName && datasetName) {
      if (tempImages.hasOwnProperty(variableName + depthIndex)) {
        dispatch(setImage(tempImages[variableName + depthIndex]));
      } else {
        if (datasetId) {
          dispatch(
            generateImage({
              dataset: datasetName,
              variable: variableName,
              depth_index: depthIndex,
              time_index: 0, // TODO: Add time index selection
            })
          );
          dispatch(getLatLon({ dataset: datasetId }));
        }
      }
    }
  };

  const onVariableSelect = (v: datasetVariableType[0]) => {
    const temp = [...variables];
    temp.forEach((temp_v) => {
      temp_v.checked = temp_v.variable === v.variable;
    });
    setVariables(temp);
  };

  const resizeMap = () => {};

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

  useEffect(() => {
    handlePlotClick();
  }, [depthIndex]);

  useEffect(() => {
    resizeMap();
  }, [tempImage]);

  return (
    <div className="text-nc-500 p-4 w-full">
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
        <h1 className="text-2xl">Loading...</h1>
      ) : (
        <h1 className="text-2xl">{selectedDataset?.name}</h1>
      )}

      <PanelGroup direction="horizontal" className="mt-4">
        <Panel defaultSize={50}>
          <div style={{ height: "80vh" }}>
            {variables.map((v) => {
              return (
                <CheckBox
                  key={v.variable}
                  label={v.variable + " [" + v.dimensions.length + "D]"}
                  id={v.variable}
                  checked={v.checked}
                  onChange={() => onVariableSelect(v)}
                />
              );
            })}

            <br />

            <label>Depth index : {depthIndex}</label>
            <input
              style={{
                width: "100%",
              }}
              type="range"
              disabled={loading}
              min="0"
              max={activeDataset?.info.dims["depth"]}
              value={depthIndex}
              onChange={(e) => {
                setDepthIndex(parseInt(e.target.value));
              }}
            />
          </div>
        </Panel>
        <PanelResizeHandle className="border" />
        <Panel defaultSize={50} maxSize={80}>
          <div
            style={{
              zIndex: 90,
              width: "100%",
              height: "100%",
              // position: "absolute",
            }}
          >
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
