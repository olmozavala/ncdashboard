import { useDispatch, useSelector } from "react-redux";
import { Map } from "..";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { generatePlot } from "../../redux/slices/DataSlice";

interface FourDPlotProps {
  variable: string;
  dataset: string;
  height?: number;
  width?: number;
}

const FourDPlot = (props: FourDPlotProps) => {
  const dispatch = useDispatch<AppDispatch>();
  const { plots, available_datasets } = useSelector(
    (state: RootState) => state.data
  );

  const activeDataset = available_datasets.find(
    (dataset) => dataset.id === props.dataset
  );

  const [depthIndex, setDepthIndex] = useState<number>(0);
  const [timeIndex, setTimeIndex] = useState<number>(0);

  const plot = plots[props.variable];

  useEffect(() => {
    const key = `depth_${depthIndex}_time_${timeIndex}`;
    if (
      !plot ||
      (plot && plot.images !== undefined && key in plot.images === false)
    ) {
      if (activeDataset)
        dispatch(
          generatePlot({
            lat_var: "lat",
            lon_var: "lon",
            dataset: activeDataset.id,
            variable: props.variable,
            depthIndex: depthIndex,
            timeIndex: timeIndex,
          })
        );
    }
  }, [dispatch, activeDataset, props.variable, depthIndex, timeIndex, plot]);

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
  const lat = [
    activeDataset.info.lat[0],
    activeDataset.info.lat[activeDataset.info.lat.length - 1],
  ];
  const lon = [
    activeDataset.info.lon[0],
    activeDataset.info.lon[activeDataset.info.lon.length - 1],
  ];

  return (
    <div
      style={{
        zIndex: 90,
        width: props.width || "600px",
        height: props.height || "600px",
      }}
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
          <Map
            image={images[`depth_${depthIndex}_time_${timeIndex}`]}
            lat={lat}
            lon={lon}
          />
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
              max={activeDataset.info.dims["time"] - 1}
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
        </>
      )}
    </div>
  );
};

export default FourDPlot;
