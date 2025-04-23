/**
 * Map Component
 * 
 * An OpenLayers-based map component that displays a base map with an
 * overlaid image layer. The component supports dynamic updates of the
 * image source and extent.
 * 
 * @component
 * @example
 * ```tsx
 * <Map
 *   image="path/to/image.png"
 *   lat={[minLat, maxLat]}
 *   lon={[minLon, maxLon]}
 * />
 * ```
 */

import { useEffect, useRef } from "react";
import ImageLayer from "ol/layer/Image";
import TileLayer from "ol/layer/Tile";
import View from "ol/View";
import Map from "ol/Map";
import ImageStatic from "ol/source/ImageStatic";
import { OSM } from "ol/source";
import "ol/ol.css";

/**
 * Props interface for the Map component
 * 
 * @interface MapProps
 * @property {string} image - URL of the image to display on the map
 * @property {number[]} lat - Array containing [minLat, maxLat] coordinates
 * @property {number[]} lon - Array containing [minLon, maxLon] coordinates
 */
interface MapProps {
  /** URL of the image to display on the map */
  image: string;
  /** Array containing [minLat, maxLat] coordinates */
  lat: number[];
  /** Array containing [minLon, maxLon] coordinates */
  lon: number[];
}

/**
 * Map Component
 * 
 * @param {MapProps} props - The props for the map component
 * @returns {JSX.Element} A div element containing the OpenLayers map
 */
const MapComponent = ({ image, lat, lon }: MapProps) => {
  // Refs for map elements
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<Map>(null);
  const imageLayerRef = useRef<ImageLayer<ImageStatic>>(null);

  /**
   * Initialize the map with base layer and image layer
   * Runs once on component mount
   */
  useEffect(() => {
    const baseLayer = new TileLayer({ source: new OSM() });

    const imageExtent = [lon[0], lat[0], lon[1], lat[1]];
    const imageSource = new ImageStatic({
      url: image,
      projection: "EPSG:4326",
      imageExtent: imageExtent,
    });

    const imageLayer = new ImageLayer({ source: imageSource });
    imageLayerRef.current = imageLayer;

    const center = [(lon[0] + lon[1]) / 2, (lat[0] + lat[1]) / 2];

    if (mapRef.current) {
      mapInstanceRef.current = new Map({
        target: mapRef.current,
        layers: [baseLayer, imageLayer],
        view: new View({
          center,
          zoom: 5,
          projection: "EPSG:4326",
        }),
      });
    }

    return () => {
      mapInstanceRef.current?.setTarget(undefined);
    };
  }, []); // Only once

  /**
   * Update the image source when props change
   * Runs when image, lat, or lon props change
   */
  useEffect(() => {
    if (imageLayerRef.current && image) {
      const imageExtent = [lon[0], lat[0], lon[1], lat[1]];
      const newSource = new ImageStatic({
        url: image,
        projection: "EPSG:4326",
        imageExtent: imageExtent,
      });
      imageLayerRef.current.setSource(newSource);
    }
  }, [image, lat, lon]); // Only update the layer

  return (
    <div
      ref={mapRef}
      style={{
        height: "100%",
        width: "100%",
      }}
    />
  );
};

export default MapComponent;
