import React from "react";
import { useParams } from "react-router-dom";
const axios = require("axios").default;

export interface ExecutionProps {}

export default function Execute(props: ExecutionProps) {
  // @ts-ignore
  const { id } = useParams();

  React.useEffect(() => {
    const loadData = async function () {
      const data = await axios.get(`/app/${id}`);

      console.log(data);
    };

    loadData();
  }, []);

  if (!id) {
    return <p>Invalid</p>;
  }

  return <p>Execute</p>;
}
