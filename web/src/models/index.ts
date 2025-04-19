import customNodes from "../components/nodes";

// ErrorType enum
export enum ErrorType {
  INVALID_REQUEST = "INVALID_REQUEST",
  INVALID_ROUTE = "INVALID_ROUTE",
  INTERNAL_ERROR = "INTERNAL_ERROR",
  INVALID_DATASET = "INVALID_DATASET",
  EMPTY_DATASET_DIR = "EMPTY_DATASET_DIR",
  DATASET_NOT_FOUND = "DATASET_NOT_FOUND",
  CACHE_NOT_FOUND = "CACHE_NOT_FOUND",
  CACHE_INDEX_ERROR = "CACHE_INDEX_ERROR",
  IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND",
  SESSION_NOT_FOUND = "SESSION_NOT_FOUND",
}

// Image interface
export interface Image {
  id: string;
  dataset_id: string;
  variable: string;
  file_path: string;
}

// CachedDataset interface
export interface CachedDataset {
  id: string;
  name: string;
  description: string;
  created_at: string;
  images: Image[];
}

// CacheIndex interface
export interface CacheIndex {
  cache: CachedDataset[];
}

// SessionParams interface
export interface SessionParams {
  colorspace: string;
  variable: string;
}

// Session interface
export interface Session {
  id: string;
  parent_id?: string;
  created_at: string;
  dataset_id: string;
  params: SessionParams[];
  cache?: CachedDataset;
}

// Dataset interface
export interface Dataset {
  id: string;
  name: string;
  path: string;
}

// NC_DataBaseType interface
export interface NC_DataBaseType {
  datasets: Dataset[];
  sessions: Session[];
}

export type DatasetInfo = {
  attrs: {
    classification_level: string;
    distribution_statement: string;
    downgrade_date: string;
    classification_authority: string;
    institution: string;
    source: string;
    history: string;
    field_type: string;
    Conventions: string;
  };
  dims: Record<string, number>; // Dictionary where keys are dimension names and values are numbers
  variables_info: Record<string, string[]>; // Dictionary where keys are variable names and values are arrays of dimension names
};

export type NC_Node = {
  id: string;
  type?: keyof typeof customNodes;
  position: {
    x: number;
    y: number;
  };
  data: Parameters<(typeof customNodes)[keyof typeof customNodes]>[0]["data"];
}[];

export type datasetVariableType = {
  variable: string;
  checked: boolean;
  dimensions: string[];
}[];
