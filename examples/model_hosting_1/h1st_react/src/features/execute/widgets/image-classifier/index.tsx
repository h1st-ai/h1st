import React, { useState, useRef, useCallback, useEffect } from "react";
import { AIModel } from "features/upload_model/uploadSlice";
import UploadService from "features/upload_model/service.upload";
import { useAuth0 } from "@auth0/auth0-react";
import { useDropzone } from "react-dropzone";

export interface ImageClassiferWidgetProps {
  model: AIModel;
}

export default function ImageClassifer({ model }: ImageClassiferWidgetProps) {
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState([]);
  const [previewSrc, setPreviewSrc] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);
  const previewImgEl = useRef(null);

  const { getAccessTokenSilently } = useAuth0();

  const [isInputMounted, setIsInputMounted] = useState(true);

  const onDrop = useCallback((acceptedFiles) => {
    var reader = new FileReader();

    reader.onload = function (e) {
      // @ts-ignore
      setPreviewSrc(e.target.result);
    };

    reader.readAsDataURL(acceptedFiles[0]);
  }, []);

  const { acceptedFiles, getRootProps, getInputProps, inputRef } = useDropzone({
    onDrop,
    accept: "image/jpeg, image/png",
  });

  useEffect(
    function remountInput() {
      if (!isInputMounted) {
        setIsInputMounted(true);
      }
    },
    [isInputMounted]
  );

  if (!model) {
    return null;
  }

  const reset = () => {
    UploadService.cancelRequest();
    setPreviewSrc(0);
    acceptedFiles.splice(0);
  };

  const submit = async () => {
    const token = await getAccessTokenSilently();

    const res = await UploadService.upload(
      `/api/app/${model.model_id}/execute/img_classifer/`,
      { file: acceptedFiles[0], model_id: model.model_id },
      (event) => {
        const prog = Math.round((100 * event.loaded) / event.total);
        console.log(prog);
        setProgress(prog);
      },
      token
    );

    if (res.data.status === "OK") {
      setResult(res.data.result.slice(0, 3));
      // set the uploaded file here
      // setUploadedFile(result.data.id);
    }
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200">
      <div className="px-4 py-5 sm:px-6">
        <h1 className="text-xl font-bold leading-7 text-gray-900 sm:text-2xl sm:truncate">
          {model.name}
        </h1>
        <p className="mt-2 text-sm sm:text-md font-medium text-gray-500 hover:text-gray-700">
          {model.description}
        </p>
      </div>
      <div className="px-4 py-5 sm:p-6">
        {acceptedFiles.length > 0 && previewSrc && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-2">
            <div>
              <img
                className="sm:rounded-lg"
                // @ts-ignore
                src={previewSrc}
                width="100%"
                height="100%"
                ref={previewImgEl}
                alt="input"
              />
            </div>
            <div>
              {result.length > 0 && (
                <div>
                  <h3>Results</h3>
                  <ul>
                    {result.map((r) => {
                      return (
                        <div>
                          {r[0]} {Number(r[1] * 100).toFixed(2)}%
                        </div>
                      );
                    })}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {acceptedFiles.length === 0 && (
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-6">
              <div
                {...getRootProps({
                  className:
                    "hover:border-blue-500 dropzone mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-gray-300 border-dashed rounded-md",
                })}
              >
                <div className="space-y-1 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400 fill-current"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <g clipPath="url(#clip0)">
                      <path d="M6.5 11C5.21442 11 3.95772 11.3812 2.8888 12.0954C1.81988 12.8097 0.986756 13.8248 0.494786 15.0126C0.00281635 16.2003 -0.125905 17.5072 0.124899 18.7681C0.375703 20.029 0.994768 21.1872 1.90381 22.0962C2.81285 23.0052 3.97104 23.6243 5.23192 23.8751C6.49279 24.1259 7.79973 23.9972 8.98744 23.5052C10.1752 23.0132 11.1903 22.1801 11.9046 21.1112C12.6188 20.0423 13 18.7856 13 17.5C12.9979 15.7767 12.3124 14.1247 11.0939 12.9061C9.87533 11.6876 8.22326 11.0021 6.5 11ZM8.891 16.688C8.94976 16.7616 8.98655 16.8503 8.99713 16.9438C9.0077 17.0374 8.99164 17.1321 8.95078 17.2169C8.90993 17.3018 8.84594 17.3734 8.76619 17.4234C8.68644 17.4735 8.59417 17.5001 8.5 17.5H7.75C7.6837 17.5 7.62011 17.5263 7.57323 17.5732C7.52634 17.6201 7.5 17.6837 7.5 17.75V20.5C7.5 20.7652 7.39465 21.0196 7.20711 21.2071C7.01957 21.3946 6.76522 21.5 6.5 21.5C6.23479 21.5 5.98043 21.3946 5.7929 21.2071C5.60536 21.0196 5.5 20.7652 5.5 20.5V17.75C5.5 17.6837 5.47366 17.6201 5.42678 17.5732C5.3799 17.5263 5.31631 17.5 5.25 17.5H4.5C4.40583 17.5001 4.31356 17.4735 4.23381 17.4234C4.15406 17.3734 4.09008 17.3018 4.04922 17.2169C4.00837 17.1321 3.9923 17.0374 4.00288 16.9438C4.01345 16.8503 4.05024 16.7616 4.109 16.688L6.109 14.188C6.15754 14.1319 6.21757 14.0869 6.28504 14.0561C6.35251 14.0252 6.42582 14.0092 6.5 14.0092C6.57419 14.0092 6.6475 14.0252 6.71497 14.0561C6.78243 14.0869 6.84247 14.1319 6.891 14.188L8.891 16.688Z" />
                      <path d="M6.5 11C5.21442 11 3.95772 11.3812 2.8888 12.0954C1.81988 12.8097 0.986756 13.8248 0.494786 15.0126C0.00281635 16.2003 -0.125905 17.5072 0.124899 18.7681C0.375703 20.029 0.994768 21.1872 1.90381 22.0962C2.81285 23.0052 3.97104 23.6243 5.23192 23.8751C6.49279 24.1259 7.79973 23.9972 8.98744 23.5052C10.1752 23.0132 11.1903 22.1801 11.9046 21.1112C12.6188 20.0423 13 18.7856 13 17.5C12.9979 15.7767 12.3124 14.1247 11.0939 12.9061C9.87533 11.6876 8.22326 11.0021 6.5 11ZM8.891 16.688C8.94976 16.7616 8.98655 16.8503 8.99713 16.9438C9.0077 17.0374 8.99164 17.1321 8.95078 17.2169C8.90993 17.3018 8.84594 17.3734 8.76619 17.4234C8.68644 17.4735 8.59417 17.5001 8.5 17.5H7.75C7.6837 17.5 7.62011 17.5263 7.57323 17.5732C7.52634 17.6201 7.5 17.6837 7.5 17.75V20.5C7.5 20.7652 7.39465 21.0196 7.20711 21.2071C7.01957 21.3946 6.76522 21.5 6.5 21.5C6.23479 21.5 5.98043 21.3946 5.7929 21.2071C5.60536 21.0196 5.5 20.7652 5.5 20.5V17.75C5.5 17.6837 5.47366 17.6201 5.42678 17.5732C5.3799 17.5263 5.31631 17.5 5.25 17.5H4.5C4.40583 17.5001 4.31356 17.4735 4.23381 17.4234C4.15406 17.3734 4.09008 17.3018 4.04922 17.2169C4.00837 17.1321 3.9923 17.0374 4.00288 16.9438C4.01345 16.8503 4.05024 16.7616 4.109 16.688L6.109 14.188C6.15754 14.1319 6.21757 14.0869 6.28504 14.0561C6.35251 14.0252 6.42582 14.0092 6.5 14.0092C6.57419 14.0092 6.6475 14.0252 6.71497 14.0561C6.78243 14.0869 6.84247 14.1319 6.891 14.188L8.891 16.688Z" />
                      <path d="M24 4.414C23.9999 3.88361 23.7891 3.37499 23.414 3L21 0.586C20.8142 0.400151 20.5936 0.252738 20.3508 0.152189C20.108 0.0516398 19.8478 -7.51847e-05 19.585 8.20398e-08H8.00001C7.46958 8.20398e-08 6.96087 0.210714 6.58579 0.585787C6.21072 0.960859 6.00001 1.46957 6.00001 2V9.275C5.99946 9.34009 6.02453 9.40279 6.06981 9.44956C6.11508 9.49633 6.17693 9.52343 6.24201 9.525C6.60801 9.531 7.28001 9.558 7.72701 9.608C7.76168 9.61183 7.79676 9.60825 7.82994 9.59748C7.86312 9.58672 7.89363 9.56903 7.91944 9.54557C7.94526 9.52212 7.9658 9.49345 7.97969 9.46145C7.99358 9.42946 8.0005 9.39488 8.00001 9.36V2.5C8.00001 2.36739 8.05269 2.24021 8.14645 2.14645C8.24022 2.05268 8.3674 2 8.50001 2H19.379C19.5114 2.00003 19.6383 2.05253 19.732 2.146L21.854 4.268C21.9475 4.36171 22 4.48865 22 4.621V18C22 18.1326 21.9473 18.2598 21.8536 18.3536C21.7598 18.4473 21.6326 18.5 21.5 18.5H14.642C14.5834 18.5004 14.5268 18.5217 14.4825 18.5603C14.4383 18.5988 14.4094 18.6519 14.401 18.71C14.3259 19.2064 14.2041 19.6946 14.037 20.168C14.0229 20.2049 14.018 20.2448 14.0227 20.284C14.0274 20.3233 14.0416 20.3608 14.064 20.3934C14.0865 20.426 14.1165 20.4526 14.1515 20.471C14.1865 20.4894 14.2255 20.499 14.265 20.499H22C22.5304 20.499 23.0392 20.2883 23.4142 19.9132C23.7893 19.5381 24 19.0294 24 18.499V4.414Z" />
                      <path d="M24 4.414C23.9999 3.88361 23.7891 3.37499 23.414 3L21 0.586C20.8142 0.400151 20.5936 0.252738 20.3508 0.152189C20.108 0.0516398 19.8478 -7.51847e-05 19.585 8.20398e-08H8.00001C7.46958 8.20398e-08 6.96087 0.210714 6.58579 0.585787C6.21072 0.960859 6.00001 1.46957 6.00001 2V9.275C5.99946 9.34009 6.02453 9.40279 6.06981 9.44956C6.11508 9.49633 6.17693 9.52343 6.24201 9.525C6.60801 9.531 7.28001 9.558 7.72701 9.608C7.76168 9.61183 7.79676 9.60825 7.82994 9.59748C7.86312 9.58672 7.89363 9.56903 7.91944 9.54557C7.94526 9.52212 7.9658 9.49345 7.97969 9.46145C7.99358 9.42946 8.0005 9.39488 8.00001 9.36V2.5C8.00001 2.36739 8.05269 2.24021 8.14645 2.14645C8.24022 2.05268 8.3674 2 8.50001 2H19.379C19.5114 2.00003 19.6383 2.05253 19.732 2.146L21.854 4.268C21.9475 4.36171 22 4.48865 22 4.621V18C22 18.1326 21.9473 18.2598 21.8536 18.3536C21.7598 18.4473 21.6326 18.5 21.5 18.5H14.642C14.5834 18.5004 14.5268 18.5217 14.4825 18.5603C14.4383 18.5988 14.4094 18.6519 14.401 18.71C14.3259 19.2064 14.2041 19.6946 14.037 20.168C14.0229 20.2049 14.018 20.2448 14.0227 20.284C14.0274 20.3233 14.0416 20.3608 14.064 20.3934C14.0865 20.426 14.1165 20.4526 14.1515 20.471C14.1865 20.4894 14.2255 20.499 14.265 20.499H22C22.5304 20.499 23.0392 20.2883 23.4142 19.9132C23.7893 19.5381 24 19.0294 24 18.499V4.414Z" />
                    </g>
                    <defs>
                      <clipPath id="clip0">
                        <rect width="24" height="24" fill="white" />
                      </clipPath>
                    </defs>
                  </svg>

                  <div className="flex text-sm text-gray-600">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                    >
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        ref={fileRef}
                        {...getInputProps()}
                      />
                    </label>
                  </div>
                  <p className="text-sm text-gray-500">
                    <span className="text-blue-600">Select file</span> or drag
                    and drop a file here to upload (limit: 200Kb)
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="px-4 py-4 sm:px-6 bg-gray-50 ">
        <button
          type="submit"
          className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
          onClick={submit}
        >
          <span className="flex h-2 w-2 relative mr-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-200 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-400"></span>
          </span>
          Classify Image
        </button>

        <button
          className="ml-4 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          onClick={reset}
        >
          Reset
        </button>
      </div>
    </div>
  );

  return (
    <div className="bg-white shadow sm:rounded-lg mb-10">
      <div>
        <div className="px-4 py-5 sm:p-6">
          <h3 className="mb-5 text-lg leading-6 font-medium text-gray-900">
            Upload your image
          </h3>

          {acceptedFiles.length > 0 && previewSrc && (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-2">
              <div>
                <img
                  className="sm:rounded-lg"
                  // @ts-ignore
                  src={previewSrc}
                  width="100%"
                  height="100%"
                  ref={previewImgEl}
                  alt="input"
                />
              </div>
              <div>
                {result.length > 0 && (
                  <div>
                    <h3>Results</h3>
                    <ul>
                      {result.map((r) => {
                        return (
                          <div>
                            {r[0]} {Number(r[1] * 100).toFixed(2)}%
                          </div>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {acceptedFiles.length === 0 && (
            <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
              <div className="sm:col-span-6">
                <div
                  {...getRootProps({
                    className:
                      "hover:border-blue-500 dropzone mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-gray-300 border-dashed rounded-md",
                  })}
                >
                  <div className="space-y-1 text-center">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400 fill-current"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 0l-11 6v12.131l11 5.869 11-5.869v-12.066l-11-6.065zm-1 21.2l-8-4.268v-8.702l8 4.363v8.607zm10-4.268l-8 4.268v-9.793l-8.867-4.837 7.862-4.289 9.005 4.969v9.682zm-4.408-4.338l1.64-.917-.006.623-1.64.918.006-.624zm1.653-2.165l-1.641.919-.006.624 1.641-.918.006-.625zm0-1.19l-1.641.919-.006.624 1.641-.918.006-.625zm-3.747-.781l1.645-.96-.519-.273-1.646.959.52.274zm4.208 6.33l-.486-1.865-1.641.919-.523 2.431c-.229 1.105.422 1.31 1.311.812.886-.497 1.548-1.437 1.339-2.297zm-1.335 1.684c-.411.23-.821.262-.817-.136.005-.41.422-.852.835-1.083.407-.228.81-.25.806.165-.005.398-.415.825-.824 1.054zm-4.349-10.625l-.519-.274-1.646.96.52.274 1.645-.96zm-1.559-.826l-1.646.96.523.277 1.646-.96-.523-.277zm1.992 2.885l1.644-.958-.515-.274-1.647.958.518.274zm3.001 1.744l1.646-.96-.52-.273-1.645.959.519.274zm-6.029-5.177l-1.645.96.516.274 1.647-.959-.518-.275zm1.992 2.886l1.646-.96-.52-.274-1.645.959.519.275zm3.058 1.689l1.646-.959-.518-.274-1.646.96.518.273z" />
                    </svg>

                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                      >
                        <input
                          id="file-upload"
                          name="file-upload"
                          type="file"
                          ref={fileRef}
                          {...getInputProps()}
                        />
                      </label>
                    </div>
                    <p className="text-xs text-gray-500">
                      File size limit: 10MB
                    </p>
                    {acceptedFiles.length > 0 && (
                      <aside>
                        <h4>File</h4>
                        {/* <ul>{files}</ul> */}
                      </aside>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex p-6 border-0 border-t-2">
          <button
            type="submit"
            className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
            onClick={submit}
          >
            Classify Image
          </button>
        </div>
      </div>
    </div>
  );
}
