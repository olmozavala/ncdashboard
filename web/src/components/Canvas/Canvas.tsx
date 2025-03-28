import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  Background,
  Controls,
  ReactFlow,
  reconnectEdge,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";

import customNodes from "../nodes";
import { useCallback, useEffect, useRef } from "react";
import { NC_Node } from "../../models";

interface CanvasProps {
  nodes: NC_Node;
  edges: {
    id: string;
    source: string;
    target: string;
  }[];
  onUpdate: (n: NC_Node, e: CanvasProps["edges"]) => void;
}

const Canvas = ({
  edges: initialEdges,
  nodes: initialNodes,
  onUpdate,
}: CanvasProps) => {
  // const [nodes, setNodes] = useState(initialNodes);
  const edgeReconnectSuccessful = useRef(true);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    []
  );
  const onReconnectStart = useCallback(() => {
    edgeReconnectSuccessful.current = false;
  }, []);

  const onReconnect = useCallback((oldEdge: any, newConnection: any) => {
    edgeReconnectSuccessful.current = true;
    setEdges((els) => reconnectEdge(oldEdge, newConnection, els));
  }, []);

  const onReconnectEnd = useCallback((_: any, edge: any) => {
    if (!edgeReconnectSuccessful.current) {
      setEdges((eds) => eds.filter((e) => e.id !== edge.id));
    }

    edgeReconnectSuccessful.current = true;
  }, []);

  //TODO: Find a better way to update the canvas from parent, this is a workaround
  useEffect(() => {
    setEdges(initialEdges);
    setNodes(initialNodes);
  }, [initialEdges, initialNodes]);

    useEffect(() => {
        onUpdate(nodes, edges);
    }, [nodes, edges, onUpdate]);

  return (
    <>
      <ReactFlow
        colorMode="dark"
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={customNodes}
        onConnect={onConnect}
        onReconnect={onReconnect}
        onReconnectStart={onReconnectStart}
        onReconnectEnd={onReconnectEnd}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </>
  );
};

export default Canvas;
