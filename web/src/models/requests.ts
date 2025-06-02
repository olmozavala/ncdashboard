// Request models for image generation

export interface GenerateImageRequest1D {
  /** ID of the dataset to visualize */
  dataset_id: string;
  /** The variable to visualize */
  variable: string;
}

export interface GenerateImageRequest4D extends GenerateImageRequest1D {
  /** The latitude variable to visualize */
  lat_var: string;
  /** The longitude variable to visualize */
  lon_var: string;
  /** Index for the time dimension */
  time_index: number;
  /** Index for the depth dimension */
  depth_index: number;
}

export interface GenerateImageRequest3D extends GenerateImageRequest1D {
  /** The latitude variable to visualize */
  lat_var: string;
  /** The longitude variable to visualize */
  lon_var: string;
  /** Index for the time dimension */
  time_index: number;
}
