import ModelList from "components/ModelList";
import { useAppSelector } from "app/hooks";
import { selectModels } from "features/upload_model/uploadSlice";
import AppLayout from "layouts/App";
import { PlusIcon } from "@heroicons/react/solid";
import { useHistory } from "react-router-dom";
import { APP_PREFIX } from "config";

export default function Home(props: any) {
  const models = useAppSelector(selectModels);
  const history = useHistory();

  return (
    <AppLayout>
      <header className="bg-white shadow model-list-header">
        <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="sm:text-xl text-2xl font-bold text-gray-900">
            My models
          </h1>
          {models.length > 0 && (
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              onClick={() => history.push(`/${APP_PREFIX}/upload`)}
            >
              <PlusIcon className="-ml-1 mr-3 h-5 w-5" aria-hidden="true" />
              Upload model
            </button>
          )}
        </div>
      </header>
      <main className="bg-gray-100 model-list-view">
        <div className="max-w-5xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 sm:px-0">
            <ModelList />
          </div>
        </div>
      </main>
    </AppLayout>
  );
}
