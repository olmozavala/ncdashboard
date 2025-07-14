/**
 * @module RootNavigator
 * @returns {JSX.Element} The application's navigation structure with global components
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SelectDatasetScreen, HomeScreen, DatasetScreen } from "../screens";
import { Footer, Toast, Breadcrumbs } from "../components";

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
    <BrowserRouter>
      <div className="flex flex-col min-h-screen w-full">
        {/* Global Toast Notifications */}
        <Toast />

        {/* Breadcrumbs Navigation */}
        <div className="px-4 pt-4">
          <Breadcrumbs />
        </div>

        {/* Route Outlet */}
        <div className="flex-grow">
          <Routes>
            <Route path="/">
              <Route index element={<HomeScreen />} />
            </Route>
            <Route path="/datasets" element={<SelectDatasetScreen />} />
            <Route path="/:datasetId" element={<DatasetScreen />} />
          </Routes>
        </div>

        {/* Footer always at bottom */}
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default RootNavigator;
