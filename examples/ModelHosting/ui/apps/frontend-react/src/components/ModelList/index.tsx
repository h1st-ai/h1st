import React from "react";
import { ExternalLinkIcon } from "@heroicons/react/solid";
import { useAppSelector, useAppDispatch } from "app/hooks";
import { selectModels, setModels } from "features/upload_model/uploadSlice";

const axios = require("axios").default;

export default function ModelList() {
  const models = useAppSelector(selectModels);
  const dispatch = useAppDispatch();

  React.useEffect(() => {
    const loadData = async function () {
      const result = await axios.get("/upload/");

      console.log(result);

      if (result.status === 200 && result.data.status === "OK") {
        dispatch(setModels(result.data.result));
      }
    };

    loadData();
  }, []);

  return (
    <div className="flex flex-col">
      <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
          <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Name
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Description
                  </th>
                  {/* <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Input
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Output
                  </th> */}
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Updated At
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Edit</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {models.map((model, modelIdx) => (
                  <tr
                    key={model.id}
                    className={modelIdx % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {model.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.description}
                    </td>
                    {/* <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.model_input}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.output}
                    </td> */}
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.updated_at}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex">
                      <a
                        href={`/application/${model.id}/execute`}
                        className="w-5 h-5 text-gray-500 mr-4"
                      >
                        <ExternalLinkIcon className="w-5 h-5 text-grey-100" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
