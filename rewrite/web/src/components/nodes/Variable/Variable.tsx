import { Handle, Position } from "@xyflow/react";

interface VariableNodeProps {
  data: {
    variable: string;
    dims: string[];
  };
  isConnectable?: boolean;
}

function VariableNode({ data, isConnectable }: VariableNodeProps) {
  return (
    <div className="react-flow__node-default" style={{ padding: 0 }}>
      <div
        className="border-b-[1px]"
        style={{ backgroundColor: "rgba(0,0,0,0.2)", padding: "0.5rem 0" }}
      >
        <h1 className="text-nc-500 text-xs m-0">Variable</h1>
      </div>
      <div className="p-2">
        <span className="font-bold text-sm">{data.variable}</span>
        <p className="text-nc-300">{data.dims.join(",")}</p>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        isConnectable={isConnectable}
      />
    </div>
  );
}

export default VariableNode;
