import React, {
  useState,
  useRef,
  useCallback,
  useEffect,
  Fragment,
} from "react";
import { AIModel } from "features/upload_model/uploadSlice";
import UploadService from "features/upload_model/service.upload";
import { useAuth0 } from "@auth0/auth0-react";
import { useDropzone } from "react-dropzone";
import klass from "classnames";
import { XCircleIcon } from "@heroicons/react/solid";
import styles from "./styles.module.css";

const numeral = require("numeral");
export interface ImageClassiferWidgetProps {
  model: AIModel;
}

export default function ImageClassifer({ model }: ImageClassiferWidgetProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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
    setResult([]);
    setError(null);
    setLoading(false);
  };

  const submit = async () => {
    setLoading(true);
    const token = await getAccessTokenSilently();
    let res = null;

    try {
      res = await UploadService.upload(
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
        setResult(res.data.result.slice(0, 5));
        // set the uploaded file here
        // setUploadedFile(result.data.id);
      }
    } catch (ex) {
      console.error(ex.response);
      setError(ex.response.data);
    } finally {
      setLoading(false);
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
          <Fragment>
            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <XCircleIcon
                      className="h-5 w-5 text-red-400"
                      aria-hidden="true"
                    />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                      There was an error trying to classify the image
                    </h3>
                    <div className="mt-2 text-sm text-red-700">
                      <ul className="list-disc pl-5 space-y-1">
                        {/* @ts-ignore */}
                        <li>{error.message}</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div className="grid grid-cols-1 gap-0 sm:grid-cols-2 lg:grid-cols-2 bg-gray-100">
              <div className="flex item-center bg-gray-200">
                <img
                  className="self-center"
                  // @ts-ignore
                  src={previewSrc}
                  width="100%"
                  height="auto"
                  ref={previewImgEl}
                  alt="input"
                />
              </div>
              <div className="p-6 text-sm">
                <h3 className="font-bold">Input:</h3>
                <ul className="">
                  {acceptedFiles.map((file) => (
                    // @ts-ignore
                    <li key={file.path}>
                      {/* @ts-ignore */}
                      {file.path} ({numeral(file.size).format("0b")})
                    </li>
                  ))}
                </ul>
                {result.length > 0 && (
                  <div className="mt-4">
                    <h3 className="font-bold">Result:</h3>
                    <ul>
                      {result.map((r) => {
                        return (
                          <li>
                            <div
                              className="relative bg-blue-900 py-5 px-1 rounded-sm my-2"
                              style={{ width: `${r[1] * 100}%` }}
                            >
                              <span
                                className={klass(
                                  {
                                    "right-2 text-xs text-white ":
                                      r[1] * 100 > 40,
                                    [styles["overflown-result"]]:
                                      r[1] * 100 <= 40,
                                  },
                                  "flex absolute inset-y-0 items-center whitespace-nowrap"
                                )}
                              >
                                {r[0]} ({Number(r[1] * 100).toFixed(2)}%)
                              </span>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </Fragment>
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
                    and drop a file here to upload (limit: 200KB)
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
          className="disabled:opacity-50 mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
          onClick={submit}
          disabled={loading || acceptedFiles.length === 0}
        >
          {loading && (
            <span className="flex h-2 w-2 relative mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-200 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-400"></span>
            </span>
          )}
          Classify Image
        </button>

        <button
          className="lg:ml-4 lg:mt-0 mt-4 w-full inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm items-center justify-center"
          onClick={reset}
        >
          Reset
        </button>
      </div>
    </div>
  );
}
