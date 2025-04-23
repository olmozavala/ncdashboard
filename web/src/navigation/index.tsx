/**
 * @module RootNavigator
 * @returns {JSX.Element} The application's navigation structure with global components
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SelectDatasetScreen, HomeScreen, DatasetScreen } from "../screens";
import { Footer, Toast } from "../components";

/**
 * Main navigation component that sets up the application's routing structure and global components.
 * 
 * Routes:
 * - / (HomeScreen): Main landing page
 * - /datasets (SelectDatasetScreen): Dataset selection interface
 * - /:datasetId (DatasetScreen): Individual dataset view with dynamic parameter
 * 
 * Global Components:
 * - Toast: Displays notification messages with different types (error, info, success)
 * - Footer: Shows application version and copyright information
 */
const RootNavigator = () => {
  return (
    <div className="flex flex-row">
      <Toast />
      <BrowserRouter>
        <Routes>
          <Route path="/">
            <Route index element={<HomeScreen />} />
          </Route>
          <Route path="/datasets" element={<SelectDatasetScreen />} />
          <Route path="/:datasetId" element={<DatasetScreen />} />
        </Routes>
      </BrowserRouter>
      <Footer />
    </div>
  );
};

export default RootNavigator;
