import React from 'react';

import { store } from './redux/store';
import { Provider } from 'react-redux'
import RootNavigator from './navigation';

function App() {
  return (
    <Provider store={store}>
      <RootNavigator />
    </Provider>
  );
}

export default App;
