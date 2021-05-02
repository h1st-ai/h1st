import React from "react";
import { AIModel } from "features/upload_model/uploadSlice";

import { useDropzone } from "react-dropzone";

export interface ImageClassiferWidgetProps {
  model: AIModel;
}

export default function ImageClassifer({ model }: ImageClassiferWidgetProps) {
  const { name, type } = JSON.parse(model.input)[0];

  if (!name || !type) {
    return <p>Invalid input</p>;
  }

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Upload your image
        </h3>

        <button
          type="submit"
          className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
        >
          Upload
        </button>
      </div>
    </div>
  );
}
