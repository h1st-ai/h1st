import { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useHistory } from "react-router";
import { APP_PREFIX } from "config";

export default function AuthCallback() {
  const { handleRedirectCallback } = useAuth0();
  const history = useHistory();

  // handleRedirectCallback().then((a) => {
  //   console.log("a", a);
  // });

  // handleRedirect();

  useEffect(() => {
    async function handleRedirect() {
      try {
        const { appState } = await handleRedirectCallback();
        history.push(appState.returnTo);
      } catch (ex) {
        console.error(ex);
        history.push(`/${APP_PREFIX}`);
      }
    }

    handleRedirect();
  }, [handleRedirectCallback, history]);

  return null;
}
