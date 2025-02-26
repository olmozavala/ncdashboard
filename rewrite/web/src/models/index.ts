
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
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
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
