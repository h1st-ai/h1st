import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  useLocation,
} from "react-router-dom";
import Home from "views/home";
import Execute from "views/execute";
import Four0four from "views/404";

const APP_PREFIX = "aicargo";

export default function App() {
  return (
    <Router>
      <Switch>
        <Route path={`/${APP_PREFIX}`} exact={true}>
          <Home />
        </Route>
        <Route path={`/${APP_PREFIX}/application/:id/execute`}>
          <Execute />
        </Route>
        <Route path="*">
          <NoMatch />
        </Route>
      </Switch>
    </Router>
  );
}

function NoMatch() {
  // let location = useLocation();

  return <Four0four />;
}
