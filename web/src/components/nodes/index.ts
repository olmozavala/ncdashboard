/**
 * @module nodes
 * @description Exports custom node components for the React Flow canvas
 * 
 * This module provides:
 * - VariableNode: For selecting and configuring dataset variables
 * - RenderNode: For rendering and visualizing selected variables
 * 
 * These nodes are used in the canvas to create data processing workflows.
 */

import VariableNode from "./Variable/Variable";
import RenderNode from "./Render/Render";

/**
 * Object containing all custom node components
 * 
 * @type {Object}
 * @property {React.Component} VariableNode - Component for variable selection
 * @property {React.Component} RenderNode - Component for data rendering
 */
const customNodes = {
  VariableNode: VariableNode,
  RenderNode: RenderNode,
};

export default customNodes;
export { VariableNode, RenderNode };
