import React, { useEffect, useRef } from "react";
import ImageLayer from "ol/layer/Image";
import TileLayer from "ol/layer/Tile";
import View from "ol/View";
import Map from "ol/Map";
import ImageStatic from "ol/source/ImageStatic";
import { OSM } from "ol/source";
import "ol/ol.css";

interface MapProps {
  image: string;
  lat: number[]; // [minLat, maxLat]
  lon: number[]; // [minLon, maxLon]
}

const MapComponent = ({ image, lat, lon }: MapProps) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<Map>(null);
  const imageLayerRef = useRef<ImageLayer<ImageStatic>>(null);

  // Create map once on mount
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

  // Update image source when props change
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
