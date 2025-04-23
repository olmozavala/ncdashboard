/**
 * @module Toast
 * @description A reusable toast notification component that displays messages with different types (error, info, success)
 * 
 * The component:
 * - Uses Redux to manage toast state (message, visibility, type)
 * - Supports three types of notifications: error (red), info (blue), success (green)
 * - Animates in/out with opacity transitions
 * - Is positioned absolutely in the top-right corner
 * 
 * @example
 * ```tsx
 * // Dispatch a toast action
 * dispatch(showToast({ message: "Operation successful", type: "success" }));
 * ```
 */

import { useSelector } from "react-redux";
import { RootState } from "../../redux/store";

/**
 * Toast component that displays notification messages with different styles based on type
 * 
 * @component
 * @returns {JSX.Element} A styled div containing the toast message
 * 
 * @example
 * ```tsx
 * <Toast />
 * ```
 */
const Toast = () => {
  /**
   * Get toast state from Redux store
   * @type {Object}
   * @property {string} message - The message to display
   * @property {boolean} show - Whether the toast is visible
   * @property {string} type - The type of toast (error, info, success)
   */
  const { message, show, type } = useSelector(
    (state: RootState) => state.toast
  );

  return (
    <div
      className={`absolute ${
        { error: "bg-red-800", info: "bg-sky-700", success: "bg-green-700" }[
          type
        ]
      } z-50 w-80 text-white text-center px-4 py-4 rounded-md mt-4 ml-4 transition right-12 duration-300 ${
        show ? "" : "opacity-0"
      }`}
    >
      {message}
    </div>
  );
};

export default Toast;
