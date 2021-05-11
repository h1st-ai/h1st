import React from "react";
import { ExternalLinkIcon } from "@heroicons/react/solid";
import { useAppSelector, useAppDispatch } from "app/hooks";
import {
  selectModels,
  setModels,
  showUploadForm,
} from "features/upload_model/uploadSlice";
import { useAuth0 } from "@auth0/auth0-react";
import { PlusIcon } from "@heroicons/react/solid";
import { Illustration } from "components/Illustration";

const axios = require("axios").default;

export default function ModelList() {
  const models = useAppSelector(selectModels);
  const dispatch = useAppDispatch();

  const { getAccessTokenSilently } = useAuth0();

  React.useEffect(() => {
    const loadData = async function () {
      const token = await getAccessTokenSilently();
      const result = await axios.get("api/upload/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (result.status === 200 && result.data.status === "OK") {
        dispatch(setModels(result.data.result));
      }
    };

    loadData();
  }, []);

  if (models.length === 0) {
    return (
      <div className="w-6/12 m-auto text-center mt-4">
        <p className="text-gray-500 text-lg mb-6 mt-12">
          It's a little bit empty here
        </p>
        <button
          onClick={() => dispatch(showUploadForm())}
          type="button"
          className="mb-10 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="-ml-1 mr-3 h-5 w-5" aria-hidden="true" />
          Upload model
        </button>
        <Illustration name="interact" />
      </div>
    );
  }

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
                    className="overflow-ellipsis overflow-hidden flex-wrap max-w-sm px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Description
                  </th>
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
                    <td className="overflow-ellipsis overflow-hidden flex-wrap max-w-sm px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.updated_at}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex">
                      <a
                        href={`/application/${model.model_id}/execute`}
                        className="w-5 h-5 text-gray-500 mr-4"
                        target="_blank"
                        rel="noreferrer"
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
