import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Home from "views/home";
import Execute from "views/execute";
import Four0four from "views/404";
import UploadView from "views/model-upload";
import LandingPage from "views/landing-page";
import AuthCallback from "views/auth-callback";

import { APP_PREFIX } from "config";

export default function App() {
  return (
    <Router>
      <Switch>
        <Route path={`/${APP_PREFIX}`} exact={true}>
          <LandingPage />
        </Route>
        <Route path={`/${APP_PREFIX}/dashboard`} exact={true}>
          <Home />
        </Route>
        <Route path={`/${APP_PREFIX}/upload`} exact={true}>
          <UploadView />
        </Route>
        <Route path={`/${APP_PREFIX}/application/:id/execute`}>
          <Execute />
        </Route>
        <Route path={`/${APP_PREFIX}/callback`} exact={true}>
          <AuthCallback />
        </Route>
        <Route path="*">
          <NoMatch />
        </Route>
      </Switch>
    </Router>
  );
}

function NoMatch() {
  return <Four0four />;
}
