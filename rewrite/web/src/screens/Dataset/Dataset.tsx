import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import {
  fetchDatasetInfo,
  fetchDataSets,
  generateImage,
} from "../../redux/slices/DataSlice";
import { Button, Canvas } from "../../components";
import {  listSessions } from "../../redux/slices/SessionSlice";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { datasetVariableType, NC_Node } from "../../models";
import { Edge } from "@xyflow/react";

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
    tempImage,
  } = useSelector((state: RootState) => state.data);
  const { sessions } = useSelector((state: RootState) => state.session);

  const [nodes, setNodes] = useState<NC_Node>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [variables, setVariables] = useState<datasetVariableType>([]);

  let output_nodes: typeof nodes = [];
  let output_edges: typeof edges = [];

  const selectedDataset = available_datasets.find(
    (dataset) => dataset.id === datasetId
  );

  let dataset_sessions = sessions.filter(
    (session) => session.dataset_id === datasetId
  );

  const handleVariableClick = (variable: string) => {
    setVariables(
      variables.map((v) =>
        v.variable === variable ? { ...v, checked: !v.checked } : v
      )
    );
  };

  const handlePlotClick = () => {
    for (let i = 0; i < output_edges.length; i++) {
      const source = output_edges[i].source;
      const target = output_edges[i].target;
      if (target === "render") {
        const for_render = output_nodes.find((n) => n.id === source)?.data;
        if (activeDataset && for_render && "variable" in for_render) {
          dispatch(
            generateImage({
              dataset: activeDataset.dataset.name,
              variable: for_render.variable,
              depth_index: 0,
              time_index: 0,
            })
          );
        }
      }
    }
  };

  const onCanvasUpdate = (n: NC_Node, e: Edge[]) => {
    output_nodes = n;
    output_edges = e;
  };

  useEffect(() => {
    const temp_nodes: typeof nodes = [];
    variables.forEach((v, i) => {
      temp_nodes.push({
        id: i.toString(),
        type: "VariableNode",
        position: { x: 0, y: i * 100 },
        data: { variable: v.variable, dims: v.dimensions },
      });
    });
    temp_nodes.push({
      data: { dimension: 2 },
      id: "render",
      position: { x: 200, y: 200 },
      type: "RenderNode",
    });
    setNodes(temp_nodes);
  }, [variables]);

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
        "Loading..."
      ) : (
        <h1 className="text-2xl">{selectedDataset?.name}</h1>
      )}

      <PanelGroup direction="horizontal" className="mt-4">
        <Panel defaultSize={50}>
          {/* <div className="flex flex-col gap-4 mt-8 px-4">
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
                      <p className="text-sm text-nc-400 pl-6">
                        Dims: {v.dimensions.join(",")}
                      </p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div> */}
          <div style={{ height: "80vh" }}>
            {nodes.length > 0 && (
              <Canvas edges={edges} nodes={nodes} onUpdate={onCanvasUpdate} />
            )}
          </div>
        </Panel>
        <PanelResizeHandle className="border" />
        <Panel defaultSize={50}>
          <div className="text-nc-500 p-4">
            <Button
              text="Plot"
              onClick={handlePlotClick}
              additionalClasses="px-4"
            />
            {tempImage && <img src={tempImage} alt="plot" />}
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
};

export default DatasetScreen;
