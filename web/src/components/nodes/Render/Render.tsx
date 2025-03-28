import { Handle, Position } from "@xyflow/react";

interface RenderNodeProps {
  data: {
    dimension: number;
  };
  isConnectable?: boolean;
}

function RenderNode({ data, isConnectable }: RenderNodeProps) {
  return (
    <div className="react-flow__node-default" style={{ padding: 10 }}>
      <h2>Render</h2>
      <Handle
        type="target"
        position={Position.Left}
        id="output"
        isConnectable={isConnectable}
      />
    </div>
  );
}

export default RenderNode;
