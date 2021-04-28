import React from "react";
import { XIcon } from "@heroicons/react/solid";
// import { removeModelInput } from "features/upload_model/uploadSlice";
import { useAppDispatch } from "app/hooks"; // "../../../../app/hooks";

export interface ModelInputProps {
  index: number;
}

export default function ModelInput({ index }: ModelInputProps) {
  const dispatch = useAppDispatch;
  return (
    <div>
      <div className="mt-1 relative rounded-md shadow-sm">
        <input
          type="text"
          name="model_input"
          id="model_input"
          className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-20 sm:text-sm border-gray-300 rounded-md"
          placeholder="E.g: input_image"
        />
        <div className="absolute inset-y-0 left-0 flex items-center">
          <label htmlFor="input_type" className="sr-only">
            Input type
          </label>
          <select
            id="input_type"
            name="input_type"
            className="focus:ring-indigo-500 focus:border-indigo-500 h-full py-0 pl-3 pr-7 border-transparent bg-transparent text-gray-500 sm:text-sm rounded-md"
          >
            <option>Text</option>
            <option>Image</option>
          </select>
        </div>
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          <button
            className="h-5 w-5"
            // onClick={() => dispatch(removeModelInput(index))}
          >
            <XIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
