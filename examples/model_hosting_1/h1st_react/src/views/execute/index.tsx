import React from "react";
import { useParams } from "react-router-dom";

import { useAppDispatch, useAppSelector } from "app/hooks";
import { selectModel, setModel } from "features/execute/executionSlice";
import { selectModels } from "features/upload_model/uploadSlice";

import ImageClassifierWidget from "features/execute/widgets/image-classifier";

const axios = require("axios").default;

export interface ExecutionProps {}

export default function Execute(props: ExecutionProps) {
  // @ts-ignore
  const { id } = useParams();
  const dispatch = useAppDispatch();
  const model = useAppSelector(selectModel);

  React.useEffect(() => {
    const loadData = async function () {
      const res = await axios.get(`/api/app/${id}`);

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
    return <p>Invalid application</p>;
  }

  // @ts-ignore
  if (model) {
    const { type } = model.output;
    let widget = null;

    if (type === "IMG_CLASSIFIER") {
      widget = <ImageClassifierWidget model={model} />;
    }

    return (
      <div className="md:w-1/2 md:m-auto md:mt-12 mx-4 m-auto mt-4 self-center">
        {widget}

        <div className="text-xs text-gray-500 text-center my-10">
          Powered by{" "}
          <a href="https://www.h1st.ai/" className="text-blue-500">
            Human First AI
          </a>
          . Hosted by{" "}
          <a href="https://www.aitomatic.com/" className="text-blue-500">
            Aitomatic
          </a>
        </div>
      </div>
    );
  }

  return null;
}
