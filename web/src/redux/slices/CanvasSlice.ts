/**
 * @module CanvasSlice
 * @description Manages the application's visualization canvas state
 * 
 * This slice handles:
 * - Canvas dimensions and properties
 * - Canvas interaction state
 * - Canvas rendering settings
 * - Canvas viewport management
 * 
 * The slice provides:
 * - Canvas state management
 * - Viewport control
 * - Rendering configuration
 * 
 * @see store - Main Redux store configuration
 * @see components/Canvas - Canvas component implementation
 */

import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { NC_Node } from "../../models";
import { Edge } from "@xyflow/react";

/**
 * Canvas state interface
 * 
 * Defines the structure of the canvas state:
 * - nodes: List of nodes in the canvas
 * - edges: List of edges connecting nodes
 * - width: Canvas width in pixels
 * - height: Canvas height in pixels
 * - scale: Current zoom level
 * - isDragging: Drag interaction state
 */
export interface CanvasState {
  width: number;
  height: number;
  scale: number;
  isDragging: boolean;
  nodes: NC_Node;
  edges: Edge[];
}

/**
 * Initial state for the canvas slice
 * 
 * Sets up the default values for:
 * - Empty nodes and edges
 * - Default canvas dimensions
 * - Initial zoom level
 * - No drag interaction
 */
const initialState: CanvasState = {
  width: 800,
  height: 600,
  scale: 1,
  isDragging: false,
  nodes: [],
  edges: [],
};

/**
 * Canvas slice reducer
 * 
 * Manages state updates for:
 * - Node and edge management
 * - Canvas dimensions
 * - Zoom level
 * - Interaction states
 */
export const CanvasSlice = createSlice({
  name: "canvas",
  initialState,
  reducers: {
    /**
     * Updates canvas dimensions
     * @param state - Current canvas state
     * @param action - Payload containing new dimensions
     */
    setDimensions: (state, action: PayloadAction<{ width: number; height: number }>) => {
      state.width = action.payload.width;
      state.height = action.payload.height;
    },
    /**
     * Updates canvas zoom level
     * @param state - Current canvas state
     * @param action - Payload containing new scale
     */
    setScale: (state, action: PayloadAction<number>) => {
      state.scale = action.payload;
    },
    /**
     * Updates drag interaction state
     * @param state - Current canvas state
     * @param action - Payload containing drag state
     */
    setIsDragging: (state, action: PayloadAction<boolean>) => {
      state.isDragging = action.payload;
    },
    setNodes: (state, action: PayloadAction<CanvasState["nodes"]>) => {
      state.nodes = action.payload;
    },
    setEdges: (state, action: PayloadAction<CanvasState["edges"]>) => {
      state.edges = action.payload;
    },
  },
});

// Action creators are generated for each case reducer function
export const { setDimensions, setScale, setIsDragging, setNodes, setEdges } = CanvasSlice.actions;
export default CanvasSlice.reducer;
