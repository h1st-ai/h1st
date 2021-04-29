import React, { ChangeEvent } from "react";
import { XIcon } from "@heroicons/react/solid";
import {
  removeModelInput,
  updateModelInputName,
  updateModelInputType,
} from "features/upload_model/uploadSlice";
import { useAppDispatch } from "app/hooks"; // "../../../../app/hooks";

export interface ModelInputProps {
  index: number;
  id: string;
  name: string;
}

export default function ModelInput({ index, id, name }: ModelInputProps) {
  const dispatch = useAppDispatch();

  const updateInputName = (e: ChangeEvent<HTMLInputElement>): void => {
    dispatch(updateModelInputName({ index, name: e.target.value }));
    // dispatch(updateModelInputType({ index: index, type: type }))
  };

  const updateInputType = (e: ChangeEvent<HTMLSelectElement>): void => {
    console.log(e);
    dispatch(updateModelInputType({ index: index, type: e.target.value }));
  };

  return (
    <div>
      <div className="mt-1 relative rounded-md shadow-sm">
        <input
          type="text"
          name={`${id}-input`}
          id={id}
          className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-20 sm:text-sm border-gray-300 rounded-md"
          placeholder="E.g: input_image"
          onChange={updateInputName}
          value={name}
        />
        <div className="absolute inset-y-0 left-0 flex items-center">
          <label htmlFor="input_type" className="sr-only">
            Input type
          </label>
          <select
            id={`type-${id}`}
            name="input_type"
            className="focus:ring-indigo-500 focus:border-indigo-500 h-full py-0 pl-3 pr-7 border-transparent bg-transparent text-gray-500 sm:text-sm rounded-md"
            onChange={updateInputType}
          >
            <option>Text</option>
            <option>Image</option>
          </select>
        </div>
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          <button
            className="h-5 w-5"
            onClick={() => dispatch(removeModelInput(index))}
          >
            <XIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
