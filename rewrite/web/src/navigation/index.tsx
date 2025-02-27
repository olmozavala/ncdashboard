import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SelectDatasetScreen, HomeScreen, DatasetScreen } from "../screens";
import { Footer, Toast } from "../components";

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
