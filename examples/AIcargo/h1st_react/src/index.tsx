import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import { store } from "./app/store";
import { Provider } from "react-redux";
import * as serviceWorker from "./serviceWorker";
import { Auth0Provider } from "@auth0/auth0-react";
import { APP_PREFIX } from "config";
// import { createBrowserHistory } from "history";

// const history = createBrowserHistory();

// const onRedirectCallback = (appState: any) => {
//   setTimeout(() => {
//     history.push(
//       appState && appState.returnTo
//         ? appState.returnTo
//         : window.location.pathname
//     );
//   }, 0);
// };

ReactDOM.render(
  <Auth0Provider
    domain="aitomatic.us.auth0.com"
    clientId="RlwK2ZrhU2HL9Qx91uIZ6v9WKrsxfV96"
    audience="https://model-hosting.aitomatic.com/api"
    redirectUri={`${window.location.origin}/${APP_PREFIX}/callback`}
    // onRedirectCallback={onRedirectCallback}
    // redirectUri={`${window.location.origin}/${APP_PREFIX}`}
  >
    <React.StrictMode>
      <Provider store={store}>
        <App />
      </Provider>
    </React.StrictMode>
  </Auth0Provider>,
  document.getElementById("root")
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
