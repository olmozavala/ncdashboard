import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomeScreen } from "../screens";

const RootNavigator = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/">
          <Route index element={<HomeScreen />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default RootNavigator;