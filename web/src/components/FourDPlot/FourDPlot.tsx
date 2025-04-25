import { useDispatch, useSelector } from "react-redux";
import { Map } from "..";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { generatePlot } from "../../redux/slices/DataSlice";

interface FourDPlotProps {
  variable: string;
  dataset: string;
}

const FourDPlot = (props: FourDPlotProps) => {
  const dispatch = useDispatch<AppDispatch>();
  const { plots, available_datasets } = useSelector(
    (state: RootState) => state.data
  );

  const activeDataset = available_datasets.find(
    (dataset) => dataset.id === props.dataset
  );

  if (!activeDataset) {
    return <p>No active dataset found.</p>;
  }

  if (!activeDataset.info) {
    return <p>Loading dataset info...</p>;
  }

  const [imageIndex, setImageIndex] = useState<number>(0);
  const plot = plots[props.variable];

  useEffect(() => {
    if (!plot || !plot.images || plot.images.length === 0) {
      dispatch(
        generatePlot({
          dataset: activeDataset.id,
          variable: props.variable,
          dimension: 4,
        })
      );
    }
  }, [dispatch, activeDataset.name, props.variable]);

  if (props.variable in plots === false) {
    return <p>{props.variable} not ready yet.</p>;
  }

  const images = plots[props.variable].images;

  if (plot.loading) {
    return (
      <div
        style={{ zIndex: 90, width: "600px", height: "600px" }}
        className="bg-gray-800"
      >
        <h3 className="text-xl align-center">{props.variable}</h3>
        <div className="flex items-center justify-center align-middle h-full">
          <div className="w-4 h-4 border-4 border-t-transparent border-nc-500 rounded-full animate-spin"></div>
          <p className="ml-2">Loading {plot.progress} %</p>
        </div>
      </div>
    );
  }

  if (!images || images.length === 0) {
    return <p>Loading images for {props.variable}</p>;
  }

  const lat = [
    activeDataset.info.lat[0],
    activeDataset.info.lat[activeDataset.info.lat.length - 1],
  ];
  const lon = [
    activeDataset.info.lon[0],
    activeDataset.info.lon[activeDataset.info.lon.length - 1],
  ];
  return (
    <div style={{ zIndex: 90, width: "600px", height: "600px" }}>
      {images && images.length > 0 ? (
        <>
          <p className="text-xl">{props.variable}</p>
          <Map image={images[imageIndex]} lat={lat} lon={lon} />
          <label>Depth Index: </label>
          <input
            type="range"
            min={0}
            max={images.length - 1}
            value={imageIndex}
            onChange={(e) => setImageIndex(parseInt(e.target.value))}
            className="w-full"
          />
        </>
      ) : null}
    </div>
  );
};

export default FourDPlot;
