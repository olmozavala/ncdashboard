import React from 'react';
import { Link, useLocation, useParams } from "react-router-dom";
import { useSelector } from "react-redux";
import { RootState } from "../../redux/store";

interface Crumb {
  label: string;
  path?: string;
}

interface BreadcrumbsProps {
  /** Additional breadcrumb segments to append after the automatic route-based crumbs */
  extra?: Crumb[];
}

/**
 * Breadcrumbs Navigation Component
 *
 * Automatically builds breadcrumbs based on the current route and accepts
 * optional extra segments (e.g., variable, depth index) for finer-grained
 * navigation context inside modals or nested components.
 */
const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ extra = [] }) => {
  const location = useLocation();
  const { datasetId } = useParams();
  const { available_datasets } = useSelector((state: RootState) => state.data);

  // Build base crumbs from route
  const crumbs: Crumb[] = [{ label: "Home", path: "/" }];

  // Add "Datasets" crumb if we are on datasets page or dataset detail
  if (location.pathname.startsWith("/datasets") || datasetId) {
    crumbs.push({ label: "Datasets", path: "/datasets" });
  }

  // If a dataset is selected, add its name
  if (datasetId) {
    const datasetNameRaw =
      available_datasets.find((d) => d.id === datasetId)?.name || datasetId;
    // If the dataset name looks like a path, keep only the last segment
    const datasetName = datasetNameRaw.includes("/")
      ? (datasetNameRaw.split("/").pop() || datasetNameRaw)
      : datasetNameRaw;
    crumbs.push({ label: datasetName, path: `/${datasetId}` });
  }

  // Append any extra crumbs supplied by parent component
  crumbs.push(...extra);

  return (
    <nav className="text-sm text-gray-300 mb-4" aria-label="Breadcrumb">
      {crumbs.map((crumb, idx) => (
        <span key={idx} className="inline-flex items-center">
          {crumb.path ? (
            <Link to={crumb.path} className="hover:underline">
              {crumb.label}
            </Link>
          ) : (
            <span className="text-gray-400">{crumb.label}</span>
          )}
          {idx < crumbs.length - 1 && (
            <span className="mx-1 select-none">&gt;</span>
          )}
        </span>
      ))}
    </nav>
  );
};

export default Breadcrumbs; 