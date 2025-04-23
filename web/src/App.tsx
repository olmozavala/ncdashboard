/**
 * Main application component that serves as the root of the React application.
 * This component sets up the Redux store provider and the application's navigation structure.
 * 
 * The application uses:
 * - Redux for state management with multiple slices (auth, data, toast, session, canvas)
 * - React Router for navigation between different screens
 * - A custom navigation component (RootNavigator) that handles routing
 * 
 * @module App
 * @returns {JSX.Element} The root application component wrapped in Redux Provider
 */

import { store } from './redux/store';
import { Provider } from 'react-redux'
import RootNavigator from './navigation';

/**
 * Root application component that wraps the entire application with necessary providers
 * and sets up the main navigation structure.
 * 
 * The component:
 * 1. Provides Redux store access to all child components
 * 2. Renders the RootNavigator which handles all routing
 * 3. Maintains global state through Redux slices for:
 *    - Authentication (AuthSlice)
 *    - Data management (DataSlice)
 *    - Toast notifications (ToastSlice)
 *    - Session management (SessionsSlice)
 *    - Canvas state (CanvasSlice)
 */
function App() {
  return (
    <Provider store={store}>
      <RootNavigator />
    </Provider>
  );
}

export default App;
