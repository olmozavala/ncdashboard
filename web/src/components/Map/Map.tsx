/**
 * Map Component
 * 
 * An OpenLayers-based map component that displays a base map with an
 * overlaid image layer. The component supports dynamic updates of the
 * image source and extent, and drawing functionality for transect lines.
 * 
 * @component
 * @example
 * ```tsx
 * <Map
 *   image="path/to/image.png"
 *   lat={[minLat, maxLat]}
 *   lon={[minLon, maxLon]}
 *   enableDrawing={true}
 *   onTransectDrawn={(coordinates) => console.log(coordinates)}
 * />
 * ```
 */

import { useEffect, useRef } from "react";
import ImageLayer from "ol/layer/Image";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import View from "ol/View";
import Map from "ol/Map";
import ImageStatic from "ol/source/ImageStatic";
import VectorSource from "ol/source/Vector";
import { OSM } from "ol/source";
import Draw from "ol/interaction/Draw";
import { Select } from "ol/interaction";
import { Modify } from "ol/interaction";
import { LineString } from "ol/geom";
import { Style, Stroke, Fill } from "ol/style";
import "ol/ol.css";

/**
 * Props interface for the Map component
 * 
 * @interface MapProps
 * @property {string} image - URL of the image to display on the map
 * @property {number[]} lat - Array containing [minLat, maxLat] coordinates
 * @property {number[]} lon - Array containing [minLon, maxLon] coordinates
 * @property {boolean} enableDrawing - Whether to enable drawing functionality
 * @property {(coordinates: number[][]) => void} onTransectDrawn - Callback when a transect is drawn
 * @property {boolean} clearTransect - Trigger to clear the transect line
 */
interface MapProps {
  /** URL of the image to display on the map */
  image: string;
  /** Array containing [minLat, maxLat] coordinates */
  lat: number[];
  /** Array containing [minLon, maxLon] coordinates */
  lon: number[];
  /** Whether to enable drawing functionality */
  enableDrawing?: boolean;
  /** Callback when a transect is drawn */
  onTransectDrawn?: (coordinates: number[][]) => void;
  /** Trigger to clear the transect line */
  clearTransect?: boolean;
}

/**
 * Map Component
 * 
 * @param {MapProps} props - The props for the map component
 * @returns {JSX.Element} A div element containing the OpenLayers map
 */
const MapComponent = ({ image, lat, lon, enableDrawing = false, onTransectDrawn, clearTransect = false }: MapProps) => {
  // Refs for map elements
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<Map>(null);
  const imageLayerRef = useRef<ImageLayer<ImageStatic>>(null);
  const vectorSourceRef = useRef<VectorSource>(null);
  const vectorLayerRef = useRef<VectorLayer<VectorSource>>(null);
  const drawInteractionRef = useRef<Draw>(null);
  const selectInteractionRef = useRef<Select>(null);
  const modifyInteractionRef = useRef<Modify>(null);

  /**
   * Initialize the map with base layer, image layer, and vector layer for drawing
   * Runs once on component mount
   */
  useEffect(() => {
    console.log('Map: Initializing map...');
    const baseLayer = new TileLayer({ source: new OSM() });

    const imageExtent = [lon[0], lat[0], lon[1], lat[1]];
    const imageSource = new ImageStatic({
      url: image,
      projection: "EPSG:4326",
      imageExtent: imageExtent,
    });

    const imageLayer = new ImageLayer({ source: imageSource });
    imageLayerRef.current = imageLayer;

    // Create vector source and layer for drawing
    const vectorSource = new VectorSource();
    const vectorLayer = new VectorLayer({
      source: vectorSource,
      style: new Style({
        stroke: new Stroke({
          color: '#ff0000',
          width: 3
        }),
        fill: new Fill({
          color: 'rgba(255, 0, 0, 0.1)'
        })
      })
    });
    vectorSourceRef.current = vectorSource;
    vectorLayerRef.current = vectorLayer;

    const center = [(lon[0] + lon[1]) / 2, (lat[0] + lat[1]) / 2];

    if (mapRef.current) {
      mapInstanceRef.current = new Map({
        target: mapRef.current,
        layers: [baseLayer, imageLayer, vectorLayer],
        view: new View({
          center,
          zoom: 5,
          projection: "EPSG:4326",
        }),
      });
      console.log('Map: Map initialized successfully');
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

  /**
   * Handle clearing transect line
   * Runs when clearTransect prop changes
   */
  useEffect(() => {
    if (clearTransect && vectorSourceRef.current) {
      console.log('Map: Clearing transect line');
      vectorSourceRef.current.clear();
    }
  }, [clearTransect]);

  /**
   * Handle drawing functionality
   * Runs when enableDrawing prop changes
   */
  useEffect(() => {
    console.log('Map: Drawing effect triggered, enableDrawing:', enableDrawing);
    if (!mapInstanceRef.current || !vectorSourceRef.current) {
      console.log('Map: Map or vector source not ready');
      return;
    }

    const map = mapInstanceRef.current;
    const vectorSource = vectorSourceRef.current;

    // Remove existing interactions
    if (drawInteractionRef.current) {
      console.log('Map: Removing existing draw interaction');
      map.removeInteraction(drawInteractionRef.current);
      drawInteractionRef.current = null;
    }
    if (selectInteractionRef.current) {
      console.log('Map: Removing existing select interaction');
      map.removeInteraction(selectInteractionRef.current);
      selectInteractionRef.current = null;
    }
    if (modifyInteractionRef.current) {
      console.log('Map: Removing existing modify interaction');
      map.removeInteraction(modifyInteractionRef.current);
      modifyInteractionRef.current = null;
    }

    if (enableDrawing) {
      console.log('Map: Setting up drawing interactions...');
      
      // Clear existing features when entering drawing mode
      vectorSource.clear();
      
      // Create draw interaction for lines
      const drawInteraction = new Draw({
        source: vectorSource,
        type: 'LineString',
        maxPoints: 2,
        style: new Style({
          stroke: new Stroke({
            color: '#ff0000',
            width: 3
          })
        })
      });

      // Handle when drawing ends
      drawInteraction.on('drawend', (event) => {
        console.log('Map: Draw ended, event:', event);
        const feature = event.feature;
        const geometry = feature.getGeometry();
        if (geometry && geometry instanceof LineString) {
          // The feature is already added by the Draw interaction. We only need
          // to ensure there is at most one feature. Because we cleared the
          // source right before starting the draw interaction, the current
          // feature will be the only one present.
          const coordinates = geometry.getCoordinates();
          // Convert coordinates to lat/lon format
          const latLonCoordinates = coordinates.map((coord: number[]) => [coord[1], coord[0]]);
          console.log('Map: Extracted coordinates:', latLonCoordinates);
          if (onTransectDrawn) {
            onTransectDrawn(latLonCoordinates);
          }
        }
      });

      // Create select interaction for editing existing lines
      const selectInteraction = new Select({
        style: new Style({
          stroke: new Stroke({
            color: '#00ff00',
            width: 4
          })
        })
      });

      // Create modify interaction for editing selected lines
      const modifyInteraction = new Modify({
        features: selectInteraction.getFeatures()
      });

      // Handle when modification ends
      modifyInteraction.on('modifyend', (event) => {
        console.log('Map: Modify ended, event:', event);
        event.features.forEach((feature) => {
          const geometry = feature.getGeometry();
          if (geometry && geometry instanceof LineString) {
            const coordinates = geometry.getCoordinates();
            const latLonCoordinates = coordinates.map((coord: number[]) => [coord[1], coord[0]]);
            console.log('Map: Modified coordinates:', latLonCoordinates);
            if (onTransectDrawn) {
              onTransectDrawn(latLonCoordinates);
            }
          }
        });
      });

      // Add interactions to map
      map.addInteraction(drawInteraction);
      map.addInteraction(selectInteraction);
      map.addInteraction(modifyInteraction);

      // Store references
      drawInteractionRef.current = drawInteraction;
      selectInteractionRef.current = selectInteraction;
      modifyInteractionRef.current = modifyInteraction;
      
      console.log('Map: Drawing interactions added successfully');
    }

    return () => {
      // Cleanup interactions
      if (drawInteractionRef.current) {
        map.removeInteraction(drawInteractionRef.current);
      }
      if (selectInteractionRef.current) {
        map.removeInteraction(selectInteractionRef.current);
      }
      if (modifyInteractionRef.current) {
        map.removeInteraction(modifyInteractionRef.current);
      }
    };
  }, [enableDrawing, onTransectDrawn]);

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
