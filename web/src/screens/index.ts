/**
 * @module screens
 * @description Central export file for all screen components in the application
 * 
 * This file serves as a single entry point for all screen components, providing:
 * - Simplified imports for screens throughout the application
 * - Clear visibility of available screens
 * - Easy screen discovery and usage
 * - Maintainable screen organization
 * 
 * Available screens:
 * - HomeScreen: Main landing page of the application
 * - SelectDatasetScreen: Screen for dataset selection
 * - DatasetScreen: Screen for viewing and interacting with datasets
 * 
 * Usage:
 * import { HomeScreen, SelectDatasetScreen, DatasetScreen } from '../screens';
 */

export { default as HomeScreen } from "./Home/Home"
export { default as SelectDatasetScreen } from "./SelectDataset/SelectDataset"
export { default as DatasetScreen } from "./Dataset/Dataset"