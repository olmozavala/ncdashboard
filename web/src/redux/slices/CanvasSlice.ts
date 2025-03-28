// TODO: Remove this slice if not needed
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { NC_Node } from "../../models";
import { Edge } from "@xyflow/react";

export interface CanvasState {
  nodes: NC_Node;
  edges: Edge[];
}

const initialState: CanvasState = {
  nodes: [],
  edges: [],
};

export const CanvasSlice = createSlice({
  name: "data",
  initialState,
  reducers: {
    setNodes: (state, action: PayloadAction<CanvasState["nodes"]>) => {
      state.nodes = action.payload;
    },
    setEdges: (state, action: PayloadAction<CanvasState["edges"]>) => {
      state.edges = action.payload;
    },
  },
});

// Action creators are generated for each case reducer function
export const { setEdges, setNodes } = CanvasSlice.actions;
export default CanvasSlice.reducer;
