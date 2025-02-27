import { useSelector } from "react-redux";
import { RootState } from "../../redux/store";

const Toast = () => {
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
