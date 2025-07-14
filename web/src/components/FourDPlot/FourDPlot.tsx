import { useDispatch, useSelector } from "react-redux";
import { AnimControls, Map } from "..";
import { Breadcrumbs } from "..";
import { AppDispatch, RootState } from "../../redux/store";
import { useEffect, useState } from "react";
import { generatePlot } from "../../redux/slices/DataSlice";
import axios from "axios";

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
  const [paused, setPaused] = useState(true);
  // Animation state for depth index
  const [depthPaused, setDepthPaused] = useState(true);
  const [isModal, setIsModal] = useState(false);
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [transectCoordinates, setTransectCoordinates] = useState<number[][]>([]);
  const [clearTransect, setClearTransect] = useState(false);
  const [transectImage, setTransectImage] = useState<string | null>(null);
  const [loadingTransect, setLoadingTransect] = useState<boolean>(false);
  const [invertYAxis, setInvertYAxis] = useState<boolean>(false);
  const maxTimeIndex = activeDataset && activeDataset.info && activeDataset.info.dims["time"]
    ? activeDataset.info.dims["time"] - 1
    : 0;

  // Maximum valid depth index
  const maxDepthIndex = activeDataset && activeDataset.info && activeDataset.info.dims["depth"]
    ? activeDataset.info.dims["depth"] - 1
    : 0;

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

  // Animation effect
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

  // Depth animation effect
  useEffect(() => {
    if (depthPaused) return;
    if (maxDepthIndex <= 0) return;
    const interval = setInterval(() => {
      setDepthIndex((prev) => {
        if (prev < maxDepthIndex) {
          return prev + 1;
        } else {
          setDepthPaused(true); // Stop at the end
          return prev;
        }
      });
    }, 500);
    return () => clearInterval(interval);
  }, [depthPaused, maxDepthIndex]);

  // Handlers for AnimControls
  const handlePlay = () => setPaused(false);
  const handlePause = () => setPaused(true);
  const handleNext = () => setTimeIndex((prev) => Math.min(prev + 1, maxTimeIndex));
  const handlePrev = () => setTimeIndex((prev) => Math.max(prev - 1, 0));
  const handleSkipToStart = () => setTimeIndex(0);
  const handleEnd = () => setTimeIndex(maxTimeIndex);

  // Handlers for Depth AnimControls
  const handleDepthPlay = () => setDepthPaused(false);
  const handleDepthPause = () => setDepthPaused(true);
  const handleDepthNext = () => setDepthIndex((prev) => Math.min(prev + 1, maxDepthIndex));
  const handleDepthPrev = () => setDepthIndex((prev) => Math.max(prev - 1, 0));
  const handleDepthSkipToStart = () => setDepthIndex(0);
  const handleDepthEnd = () => setDepthIndex(maxDepthIndex);

  const handleEditClick = () => {
    console.log('FourDPlot: Edit button clicked, setting modal to true');
    setIsModal(true);
  };

  const handleCloseModal = () => {
    console.log('FourDPlot: Close button clicked, setting modal to false');
    setIsModal(false);
    setIsDrawingMode(false);
  };

  const handleTransectDrawn = (coordinates: number[][]) => {
    setTransectCoordinates(coordinates);
    console.log('Transect drawn in FourDPlot:', coordinates);
    setIsDrawingMode(false);
    setTransectImage(null);
  };

  const handleEnterDrawingMode = () => {
    console.log('FourDPlot: Entering drawing mode');
    setIsDrawingMode(true);
    setTransectCoordinates([]);
    setInvertYAxis(false);
  };

  const handleExitDrawingMode = () => {
    console.log('FourDPlot: Exiting drawing mode');
    setIsDrawingMode(false);
    setTransectCoordinates([]);
  };

  const handleClearTransect = () => {
    console.log('FourDPlot: Clearing transect');
    setTransectCoordinates([]);
    setClearTransect(true);
    setTimeout(() => setClearTransect(false), 100);
    setTransectImage(null);
  };

  // Debug logging for modal state
  useEffect(() => {
    console.log('FourDPlot: Modal state changed to:', isModal);
  }, [isModal]);

  // ---------------------------------------------------------------------------
  // Effect: Fetch transect image whenever coordinates, depth, or time change
  // ---------------------------------------------------------------------------
  useEffect(() => {
    // We need exactly two points to define a transect
    if (transectCoordinates.length !== 2 || !activeDataset) {
      return;
    }

    const fetchTransect = async () => {
      try {
        setLoadingTransect(true);
        const response = await axios.post(
          `${import.meta.env.VITE_BACKEND_API_URL}/image/generate/4d/transect`,
          {
            dataset_id: activeDataset.id,
            variable: props.variable,
            start_lat: transectCoordinates[0][0],
            start_lon: transectCoordinates[0][1],
            end_lat: transectCoordinates[1][0],
            end_lon: transectCoordinates[1][1],
            time_index: timeIndex,
            depth_index: depthIndex,
            invert_y_axis: invertYAxis,
          },
          { responseType: "blob" }
        );

        const blob = new Blob([response.data], { type: "image/png" });
        const url = URL.createObjectURL(blob);
        setTransectImage(url);
      } catch (error) {
        console.error("Failed to fetch transect image", error);
        setTransectImage(null);
      } finally {
        setLoadingTransect(false);
      }
    };

    fetchTransect();
  }, [transectCoordinates, depthIndex, timeIndex, invertYAxis, activeDataset, props.variable]);

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

  const plotContent = (
    <>
      {/* Breadcrumbs specific to this plot */}
      <Breadcrumbs
        extra={[
          { label: props.variable },
          { label: `Depth ${depthIndex}` },
          { label: `Time ${timeIndex}` },
        ]}
      />
      <div className="flex justify-between items-center mb-4">
        <p className="text-xl">{props.variable}</p>
        <div className="flex gap-2">
          {isModal && !isDrawingMode && transectCoordinates.length === 0 && (
            <button
              onClick={handleEnterDrawingMode}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Draw Transect
            </button>
          )}
          {isModal && !isDrawingMode && transectCoordinates.length > 0 && (
            <>
              <button
                onClick={handleEnterDrawingMode}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                Redraw Transect
              </button>
              <button
                onClick={handleClearTransect}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clear Transect
              </button>
            </>
          )}
          {isModal && isDrawingMode && (
            <button
              onClick={handleExitDrawingMode}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Cancel Drawing
            </button>
          )}
          {!isModal && (
            <button
              onClick={handleEditClick}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </button>
          )}
          {isModal && (
            <button
              onClick={handleCloseModal}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Close
            </button>
          )}
        </div>
      </div>
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
          <div className="flex flex-col md:flex-row gap-4">
            <div
              style={{
                position: "relative",
                width: props.width || "600px",
                height: props.height || "600px",
              }}
            >
              {isDrawingMode && (
                <div className="absolute top-2 left-2 z-10 bg-green-600 text-white px-3 py-1 rounded-lg text-sm">
                  Drawing Mode Active - Click and drag to draw transect
                </div>
              )}
              <Map
                image={images[`depth_${depthIndex}_time_${timeIndex}`]}
                lat={lat}
                lon={lon}
                enableDrawing={isDrawingMode}
                onTransectDrawn={handleTransectDrawn}
                clearTransect={clearTransect}
              />
            </div>

            {isModal && transectCoordinates.length > 0 && (
              <div
                className="p-4 bg-gray-700 rounded-lg overflow-auto"
                style={{
                  // maxHeight: props.height || "600px",
                  zIndex: 100,
                }}
              >
                <h3 className="text-lg font-semibold mb-2">Transect Coordinates</h3>
                <div className="max-h-32 overflow-y-auto mb-2">
                  {transectCoordinates.map((coord, index) => (
                    <div key={index} className="text-sm">
                      Point {index + 1}: Lat {coord[0].toFixed(4)}, Lon {coord[1].toFixed(4)}
                    </div>
                  ))}
                </div>
                <label className="flex items-center gap-2 mt-2">
                  <input
                    type="checkbox"
                    className="form-checkbox text-purple-600"
                    checked={invertYAxis}
                    onChange={(e) => setInvertYAxis(e.target.checked)}
                  />
                  <span>Invert Y Axis</span>
                </label>
                {loadingTransect && (
                  <div className="flex items-center mt-4 text-sm text-gray-300">
                    <div className="w-4 h-4 border-4 border-t-transparent border-white rounded-full animate-spin mr-2"></div>
                    Generating transect plot...
                  </div>
                )}
                {transectImage && (
                  <div className="mt-4">
                    <img
                      src={transectImage}
                      alt="Transect Plot"
                      className="max-w-full h-auto border border-gray-600 rounded"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
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

          {/* Depth animation controls */}
          <AnimControls
            paused={depthPaused}
            onPlay={handleDepthPlay}
            onPause={handleDepthPause}
            onNext={handleDepthNext}
            onPrev={handleDepthPrev}
            onSkipToStart={handleDepthSkipToStart}
            onEnd={handleDepthEnd}
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
    </>
  );

  if (isModal) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity duration-300" style={{
        zIndex:100
      }}>
        <div 
          className="bg-gray-800 rounded-lg shadow-2xl transition-all duration-300 ease-in-out"
          style={{
            width: '90vw',
            height: '90vh',
            maxWidth: '1400px',
            maxHeight: '900px',
          }}
        >
          <div className="h-full overflow-auto p-6">
            {plotContent}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        zIndex: 90,
        padding: "1rem",
      }}
      className="bg-gray-800 transition-all duration-300 ease-in-out"
    >
      {plotContent}
    </div>
  );
};

export default FourDPlot;
