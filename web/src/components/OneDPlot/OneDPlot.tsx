import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { generatePlot1D } from "../../redux/slices/DataSlice";
import { AnimControls } from "..";

interface OneDPlotProps {
  variable: string;
  dataset: string;
  height?: number;
  width?: number;
}

const OneDPlot = (props: OneDPlotProps) => {
  const dispatch = useDispatch<AppDispatch>();
  const { plots, available_datasets } = useSelector(
    (state: RootState) => state.data
  );

  const activeDataset = available_datasets.find(
    (dataset) => dataset.id === props.dataset
  );

  const [depthIndex, setDepthIndex] = useState<number>(0);
  const [timeIndex, setTimeIndex] = useState<number>(0);
  const [paused, setPaused] = useState(true);
  const maxTimeIndex = activeDataset && activeDataset.info && activeDataset.info.dims["time"]
    ? activeDataset.info.dims["time"] - 1
    : 0;
  const plot = plots[props.variable];

  useEffect(() => {
    const key = `1d_time_${timeIndex}`;
    if (
      !plot ||
      (plot && plot.images !== undefined && key in plot.images === false)
    ) {
      if (activeDataset && activeDataset.info) {
        dispatch(
          generatePlot1D({
            dataset: activeDataset.id,
            variable: props.variable,
            timeIndex: timeIndex,
          })
        );
      }
    }
  }, [dispatch, activeDataset, props.variable, depthIndex, timeIndex, plot]);

  // Animation effect for timeIndex
  useEffect(() => {
    if (paused) return;
    if (maxTimeIndex <= 0) return;
    const interval = setInterval(() => {
      setTimeIndex((prev) => {
        if (prev < maxTimeIndex) {
          return prev + 1;
        } else {
          setPaused(true); // Stop at the end
          return prev;
        }
      });
    }, 500); // Adjust speed as needed
    return () => clearInterval(interval);
  }, [paused, maxTimeIndex]);

  // Handlers for AnimControls
  const handlePlay = () => setPaused(false);
  const handlePause = () => setPaused(true);
  const handleNext = () => setTimeIndex((prev) => Math.min(prev + 1, maxTimeIndex));
  const handlePrev = () => setTimeIndex((prev) => Math.max(prev - 1, 0));
  const handleSkipToStart = () => setTimeIndex(0);
  const handleEnd = () => setTimeIndex(maxTimeIndex);

  if (!activeDataset) {
    return <p>No active dataset found.</p>;
  }

  if (!activeDataset.info) {
    return <p>Loading dataset info...</p>;
  }

  if (props.variable in plots === false) {
    return <p>{props.variable} not ready yet.</p>;
  }

  const images = plot.images;
//   const lat = [
//     activeDataset.info.lat[0],
//     activeDataset.info.lat[activeDataset.info.lat.length - 1],
//   ];
//   const lon = [
//     activeDataset.info.lon[0],
//     activeDataset.info.lon[activeDataset.info.lon.length - 1],
//   ];

  return (
    <div
      style={{
        zIndex: 90,
        width: props.width || "600px",
        height: props.height || "600px",
      }}
      className="bg-gray-800"
    >
      <p className="text-xl">{props.variable}</p>
      {plot.loading && (
        <div
          style={{
            zIndex: 90,
            width: props.width || "600px",
            height: props.height || "600px",
            position: "absolute",
            opacity: 0.7,
          }}
          className="bg-gray-800"
        >
          <div className="flex items-center justify-center align-middle h-full">
            <div className="w-4 h-4 border-4 border-t-transparent border-nc-500 rounded-full animate-spin"></div>
            <p className="ml-2">Loading ...</p>
          </div>
        </div>
      )}
      {images && (
        <>
          {/* <Map image={images[`_time_${timeIndex}`]} lat={lat} lon={lon} /> */}
          <img src={images[`1d_time_${timeIndex}`]} alt="1D Plot" />
          <label>Depth Index: {depthIndex}</label>
          <input
            type="range"
            min={0}
            max={activeDataset.info.dims["depth"] - 1}
            value={depthIndex}
            onChange={(e) => setDepthIndex(parseInt(e.target.value))}
            className="w-full"
            disabled={plot.loading}
          />
          <label>Time Index: {timeIndex}</label>
          {activeDataset.info.dims["time"] - 1 > 0 ? (
            <input
              type="range"
              min={0}
              max={maxTimeIndex}
              value={timeIndex}
              onChange={(e) => setTimeIndex(parseInt(e.target.value))}
              className="w-full"
              disabled={plot.loading}
            />
          ) : (
            <span className="text-sm">
              {" "}
              (Only one value of time index available)
            </span>
          )}
          <AnimControls
            paused={paused}
            onPlay={handlePlay}
            onPause={handlePause}
            onNext={handleNext}
            onPrev={handlePrev}
            onSkipToStart={handleSkipToStart}
            onEnd={handleEnd}
          />
        </>
      )}
    </div>
  );
};

export default OneDPlot;
