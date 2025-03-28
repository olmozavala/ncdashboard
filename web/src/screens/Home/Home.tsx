import { useDispatch } from "react-redux";
import { Button } from "../../components";
import { AppDispatch } from "../../redux/store";
import { openToast } from "../../redux/slices/ToastSlice";
import { useNavigate } from "react-router-dom";

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
