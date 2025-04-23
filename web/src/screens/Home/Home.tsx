/**
 * @module HomeScreen
 * @description The landing page of the application that serves as the entry point
 * 
 * This screen:
 * - Displays the application name (NcDashboard)
 * - Provides a "Start" button that:
 *   - Shows a toast notification
 *   - Navigates to the datasets selection screen
 * - Uses Redux for state management
 * - Implements React Router for navigation
 */

import { useDispatch } from "react-redux";
import { Button } from "../../components";
import { AppDispatch } from "../../redux/store";
import { openToast } from "../../redux/slices/ToastSlice";
import { useNavigate } from "react-router-dom";

/**
 * Home screen component that serves as the main landing page
 * 
 * @returns {JSX.Element} A centered layout with the app title and a start button
 */
const HomeScreen = () => {

  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const onClidck = () => {
    dispatch(openToast({ msg: "Start is a placeholder for login", type: "info", time: 4000 }));
    navigate("/datasets")
  }

  return (
    <div className="h-screen w-screen text-nc-500 flex flex-col justify-center items-center">
      <p className="text-xl">NcDashboard</p>
      <div className="mt-4">
        <Button text="Start" onClick={onClidck} />
      </div>
    </div>
  );
};

export default HomeScreen;
