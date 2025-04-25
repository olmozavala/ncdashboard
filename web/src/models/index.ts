import customNodes from "../components/nodes";

/**
 * Enum representing different types of errors that can occur in the application.
 * Each error type corresponds to a specific error scenario in the system.
 */
export enum ErrorType {
  /** Invalid request format or parameters */
  INVALID_REQUEST = "INVALID_REQUEST",
  /** Requested route does not exist */
  INVALID_ROUTE = "INVALID_ROUTE",
  /** Internal server error */
  INTERNAL_ERROR = "INTERNAL_ERROR",
  /** Dataset format or content is invalid */
  INVALID_DATASET = "INVALID_DATASET",
  /** Dataset directory is empty */
  EMPTY_DATASET_DIR = "EMPTY_DATASET_DIR",
  /** Requested dataset not found */
  DATASET_NOT_FOUND = "DATASET_NOT_FOUND",
  /** Requested cache not found */
  CACHE_NOT_FOUND = "CACHE_NOT_FOUND",
  /** Error in cache index */
  CACHE_INDEX_ERROR = "CACHE_INDEX_ERROR",
  /** Requested image not found */
  IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND",
  /** Requested session not found */
  SESSION_NOT_FOUND = "SESSION_NOT_FOUND",
}

/**
 * Represents a processed image from a NetCDF dataset.
 * Contains metadata and file information for visualization.
 */
export interface Image {
  /** Unique identifier for the image */
  id: string;
  /** ID of the parent dataset this image belongs to */
  dataset_id: string;
  /** The variable this image represents */
  variable: string;
  /** Path to the image file in the filesystem */
  file_path: string;
}

/**
 * Represents a cached version of a dataset for improved performance.
 * Contains pre-processed images and metadata for quick access.
 */
export interface CachedDataset {
  /** Unique identifier for the cached dataset */
  id: string;
  /** Human-readable name of the dataset */
  name: string;
  /** Description of the cached dataset */
  description: string;
  /** Timestamp when the cache was created */
  created_at: string;
  /** Array of pre-processed images in the cache */
  images: Image[];
}

/**
 * Represents the index of all cached datasets.
 * Used for quick lookup and management of cached data.
 */
export interface CacheIndex {
  /** Array of all cached datasets in the system */
  cache: CachedDataset[];
}

/**
 * Represents the parameters for a visualization session.
 * Defines how data should be displayed and processed.
 */
export interface SessionParams {
  /** Color space used for visualization (e.g., 'rgb', 'grayscale') */
  colorspace: string;
  /** Variable being visualized from the dataset */
  variable: string;
}

/**
 * Represents a user session for working with datasets.
 * Contains session state, parameters, and optional cached data.
 */
export interface Session {
  /** Unique identifier for the session */
  id: string;
  /** Optional ID of the parent session if this is a child session */
  parent_id?: string;
  /** Timestamp when the session was created */
  created_at: string;
  /** ID of the dataset being used in this session */
  dataset_id: string;
  /** Array of visualization parameters for the session */
  params: SessionParams[];
  /** Optional cached dataset data for improved performance */
  cache?: CachedDataset;
}

/**
 * Represents a NetCDF dataset in the system.
 * Contains basic metadata and file information.
 */
export interface Dataset {
  /** Unique identifier for the dataset */
  id: string;
  /** Human-readable name of the dataset */
  name: string;
  /** File system path to the dataset */
  path: string;
  /** Optional description of the dataset */
  info?: DatasetInfo;
}

/**
 * Represents the main database structure.
 * Contains collections of datasets and active sessions.
 */
export interface NC_DataBaseType {
  /** Array of all available datasets */
  datasets: Dataset[];
  /** Array of all active sessions */
  sessions: Session[];
}

/**
 * Contains detailed metadata about a NetCDF dataset.
 * Includes attributes, dimensions, and variable information.
 */
export type DatasetInfo = {
  /** Dataset attributes and metadata */
  attrs: {
    /** Classification level of the data */
    classification_level: string;
    /** Distribution statement for the data */
    distribution_statement: string;
    /** Date when the data can be downgraded */
    downgrade_date: string;
    /** Authority responsible for classification */
    classification_authority: string;
    /** Institution that produced the data */
    institution: string;
    /** Source of the data */
    source: string;
    /** History of the data processing */
    history: string;
    /** Type of field in the dataset */
    field_type: string;
    /** NetCDF conventions used */
    Conventions: string;
  };
  lat: number[];
  lon: number[];
  /** Dictionary of dimension names and their sizes */
  dims: Record<string, number>;
  /** Dictionary of variable names and their dimension names */
  variables_info: Record<string, datasetVariableType>;
};

/**
 * Represents a node in the visualization graph.
 * Used for building interactive data processing workflows.
 */
export type NC_Node = {
  /** Unique identifier for the node */
  id: string;
  /** Optional type of the node from customNodes */
  type?: keyof typeof customNodes;
  /** Position of the node in the visualization */
  position: {
    /** X-coordinate of the node */
    x: number;
    /** Y-coordinate of the node */
    y: number;
  };
  /** Data associated with the node */
  data: Parameters<(typeof customNodes)[keyof typeof customNodes]>[0]["data"];
}[];

/**
 * Represents variable information for a dataset.
 * Used for managing variable selection and display.
 */
export type datasetVariableType = {
  /** Whether the variable is selected/checked */
  checked: boolean;
  /** Array of dimension names for this variable */
  dimensions: string[];
};


// export interface Plot {
//   type: "1D" | "2D" | "3D" | "4D";
//   variable: string;
//   images: {
//     [key: string]: {
//       depth: number;
//       time: number;
//       image: string;
//     }[];
//   }[];
//   depth: number;
//   time: number;
//   loading: boolean;
//   error: boolean;
//   lat: number[];
//   lon: number[];
//   dataset: string;
// }

export interface Plot {
  dataset: string;
  variable: string;
  loading: boolean;
  error: boolean;
  images?: string[];
  progress: number;
}
