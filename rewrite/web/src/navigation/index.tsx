import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomeScreen } from "../screens";
import { SideBar } from "../components";

const RootNavigator = () => {
  return (
    <div className="flex flex-row">
      <SideBar />
      <BrowserRouter>
        <Routes>
          <Route path="/">
            <Route index element={<HomeScreen />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
};

export default RootNavigator;