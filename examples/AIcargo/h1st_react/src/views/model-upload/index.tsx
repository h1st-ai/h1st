import React from "react";

import UploadModelForm from "features/upload_model/Upload";
import AppLayout from "layouts/App";
import { useHistory } from "react-router";
import { APP_PREFIX } from "config";

export default function UploadView(props: any) {
  const history = useHistory();

  return (
    <AppLayout>
      <header className="bg-white shadow model-upload-header">
        <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="sm:text-xl text-2xl font-bold text-gray-900">
            Upload a Model
          </h1>

          <button
            type="button"
            className="inline-flex bg-gray-200 items-center px-4 py-2 border border-transparent shadow-sm text-base font-medium rounded-md"
            onClick={() => history.push(`/${APP_PREFIX}/dashboard`)}
          >
            Back to My Models
          </button>
        </div>
      </header>
      <main className="bg-gray-100 model-upload-view">
        <div className="max-w-5xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 sm:px-0">
            <UploadModelForm />
          </div>
        </div>
      </main>
    </AppLayout>
  );
}
