import React from "react";

import ModelList from "components/ModelList";
import UploadModelForm from "features/upload_model/Upload";
import { useAppSelector, useAppDispatch } from "app/hooks";
import {
  // toggleUploadState,
  selectShowModalState,
} from "features/upload_model/uploadSlice";
import AppLayout from "layouts/App";
import { PlusIcon } from "@heroicons/react/solid";
import { showUploadForm } from "features/upload_model/uploadSlice";

export default function App(props: any) {
  const showUploadModal = useAppSelector(selectShowModalState);
  const dispatch = useAppDispatch();

  return (
    <AppLayout>
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Your models</h1>
          <button
            type="button"
            className="inline-flex items-center px-6 py-3 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            onClick={() => dispatch(showUploadForm())}
          >
            <PlusIcon className="-ml-1 mr-3 h-5 w-5" aria-hidden="true" />
            New Model
          </button>
        </div>
      </header>
      <main className="bg-gray-100">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 sm:px-0">
            {!showUploadModal && <ModelList />}
            {showUploadModal && <UploadModelForm />}
          </div>
        </div>
      </main>
    </AppLayout>
  );
}
