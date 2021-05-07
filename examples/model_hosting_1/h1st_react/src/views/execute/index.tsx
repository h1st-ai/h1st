import React from "react";
import { useParams } from "react-router-dom";

import { useAppDispatch, useAppSelector } from "app/hooks";
import { selectModel, setModel } from "features/execute/executionSlice";
// import { selectModels } from "features/upload_model/uploadSlice";
import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";

import ImageClassifierWidget from "features/execute/widgets/image-classifier";

const axios = require("axios").default;

export interface ExecutionProps {}

export default function Execute(props: ExecutionProps) {
  // @ts-ignore
  const { id } = useParams();
  const dispatch = useAppDispatch();
  const model = useAppSelector(selectModel);

  const {
    getAccessTokenSilently,
    loginWithPopup,
    getAccessTokenWithPopup,
  } = useAuth0();

  React.useEffect(() => {
    const loadData = async function () {
      const access_token = await getAccessTokenSilently();

      const res = await axios.get(`/api/app/${id}`, {
        headers: {
          Authorization: `token ${access_token}`,
        },
      });

      console.log(res);

      if (res.data.status === "OK") {
        dispatch(
          setModel({
            ...res.data.model,
          })
        );
      }
    };

    loadData();
  }, []);

  if (!id) {
    return <p>Invalid</p>;
  }

  // @ts-ignore
  if (model) {
    const { type } = model.output;
    let widget = null;

    if (type == "IMG_CLASSIFIER") {
      widget = <ImageClassifierWidget model={model} />;
    }

    return (
      <div className="w-1/2 m-auto mt-10 self-center">
        <div className="text-center mb-10">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            {model.name}
          </h1>
          <p className="ml-4 text-sm font-medium text-gray-500 hover:text-gray-700">
            {model.description}
          </p>
        </div>
        {widget}
      </div>
    );
  }

  return null;
}
