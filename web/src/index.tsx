/**
 * @file index.tsx
 * @description Main entry point for the React application
 * @author Your Name
 * @date 2024
 */

// React and ReactDOM imports for rendering the application
import React from 'react';
import ReactDOM from 'react-dom/client';

// Application components and styles
import App from './App';
import './index.css';

/**
 * Root element ID where the React application will be mounted
 * @constant {string}
 */
const ROOT_ELEMENT_ID = 'root';

/**
 * Creates and renders the root React component
 * 
 * This is the main entry point of the application where:
 * 1. The root DOM element is selected
 * 2. A React root is created
 * 3. The main App component is rendered within React.StrictMode
 * 
 * @function
 * @returns {void}
 */
const root = ReactDOM.createRoot(
  document.getElementById(ROOT_ELEMENT_ID) as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

