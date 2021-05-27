import React, {
  useState,
  useRef,
  useCallback,
  useEffect,
  Fragment,
} from "react";
import { AIModel } from "features/upload_model/uploadSlice";
import UploadService from "features/upload_model/service.upload";

import { useDropzone } from "react-dropzone";
import klass from "classnames";
import { XCircleIcon } from "@heroicons/react/solid";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { getFullUrl } from "utils";
import { Link } from "react-router-dom";
import { APP_PREFIX } from "config";
import { useAuth0 } from "@auth0/auth0-react";
import LoadingIndicator from "components/loading-indicator";
import styles from "./styles.module.css";

const numeral = require("numeral");
export interface ImageClassiferWidgetProps {
  model: AIModel;
}

export enum CopyStatus {
  DEFAULT = "Copy link to this Model",
  COPIED = "Copied to clipboard",
}

export default function ImageClassifer({ model }: ImageClassiferWidgetProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loadingImage, setLoadingImage] = useState(false);
  const [result, setResult] = useState([]);
  const [previewSrc, setPreviewSrc] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);
  const previewImgEl = useRef(null);
  const { isAuthenticated } = useAuth0();

  const [copyStatus, setCopyStatus] = useState(CopyStatus.DEFAULT);

  const [isInputMounted, setIsInputMounted] = useState(true);

  const copyText = () => {
    setCopyStatus(CopyStatus.COPIED);

    setTimeout(() => setCopyStatus(CopyStatus.DEFAULT), 5000);
  };

  const onDrop = useCallback((acceptedFiles) => {
    setLoadingImage(true);
    var reader = new FileReader();

    reader.onload = function (e) {
      setLoadingImage(false);
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
    // const token = await getAccessTokenSilently();
    let res = null;

    try {
      res = await UploadService.upload(
        getFullUrl(`/api/app/${model.model_id}/execute/img_classifer/`),
        { file: acceptedFiles[0], model_id: model.model_id },
        (event) => {
          setProgress(Math.round((100 * event.loaded) / event.total));
        }
      );

      if (res.data.status === "OK") {
        setResult(res.data.result.slice(0, 3));
      }
    } catch (ex) {
      console.error(ex.response);
      setError(ex.response.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Fragment>
      <main className="text-sm p-6">
        {isAuthenticated && (
          <div className="max-w-3xl mx-auto mb-4 flex">
            <Link
              to={`/${APP_PREFIX}/dashboard`}
              className="flex items-center uppercase text-xs font-bold tracking-wide ml-auto hover:text-blue-700"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              My models
            </Link>
          </div>
        )}
        <div className="app-view-wrapper">
          <div className="flex w-full border-b border-gray-200 py-4 px-5">
            <div>
              <div className="flex items-center group relative">
                <h1 className="text-lg text-gray-800 font-semibold">
                  {model.name}
                </h1>
                {/* <button className="flex text-xs rounded-md font-semibold tracking-wide py-1 px-1.5 border border-blue-300 text-blue-700 ml-2 uppercase opacity-0  group-hover:opacity-100 group-hover:visible">
                  <span className="mr-1">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-3.5 w-3.5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </span>
                  Rename
                </button> */}
                {/* <!-- replace the name and button with the following when user clicks on Rename--> */}
                {/* <!-- <input type="text" value="Cat or not" className="text-lg pr-20 text-gray-800 border border-blue-500 font-semibold rounded" /> */}
                {/* <button className=" text-xs absolute right-2.5 top-2.5 rounded font-semibold tracking-wide py-1 px-1.5 bg-blue-700 text-white ml-2 uppercase">Save</button> --> */}
              </div>
              <div className="relative flex items-center group">
                <p className="text-gray-500">{model.description}</p>
                {/* <button className="flex text-xs rounded-md font-semibold tracking-wide py-1 px-1.5 border border-blue-300 text-blue-700 ml-2 uppercase opacity-0  group-hover:opacity-100 group-hover:visible">
                  <span className="mr-1">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-3.5 w-3.5"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </span>
                  Edit
                </button> */}
                {/* <!-- for Edit state --> */}
                {/* <!-- <textarea type="text" className="pr-20 text-base text-gray-800 border border-blue-500 font-semibold rounded">A simple cat indentification app</textarea> */}
                {/* <button className=" text-xs absolute right-2.5 top-2.5 rounded font-semibold tracking-wide py-1 px-1.5 bg-blue-700 text-white ml-2 uppercase">Save</button> --> */}
              </div>
            </div>
            <div className="ml-auto">
              <button className="text-gray-600 inline-flex font-semibold tracking-wide items-center hover:text-blue-700">
                <svg
                  xmlns=" http://www.w3.org/2000/svg"
                  className="h-4 w-4 text-gray-400 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                  />
                </svg>{" "}
                <CopyToClipboard text={window.location.href} onCopy={copyText}>
                  <button>{copyStatus}</button>
                </CopyToClipboard>
              </button>
            </div>
          </div>
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
          <div className="input-output-wrapper flex">
            <section className="ui-input py-5 pl-5 pr-2.5 w-1/2 mr-2">
              <h3 className="font-semibold text-blue-800 mb-4">Input</h3>
              {loadingImage && (
                <div
                  className={klass(
                    styles["preview-holder"],
                    "relative w-full rounded-lg flex items-center justify-center bg-gray-100 box-border"
                  )}
                >
                  <LoadingIndicator />
                </div>
              )}
              {acceptedFiles.length > 0 && previewImgEl && (
                <div>
                  <img
                    className="max-w-full rounded-lg"
                    // @ts-ignore
                    src={previewSrc}
                    ref={previewImgEl}
                    alt="input"
                  />
                </div>
              )}

              {/* <!--dropzone - remove "hidden" to show--> */}
              {(acceptedFiles.length === 0 || !setPreviewSrc) && (
                <div
                  {...getRootProps({
                    className:
                      "flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md relative",
                  })}
                >
                  {/* <!-- <span className="absolute w-64 h-2 progress-bar bottom-2"></span> --> */}

                  <div className="space-y-1 text-center text-gray-500">
                    <svg
                      className="w-12 h-12 mx-auto mb-2"
                      viewBox="0 0 64 64"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <g clip-path="url(#clip0)">
                        <path
                          d="M17.3333 25.3333C20.2789 25.3333 22.6667 22.9455 22.6667 20C22.6667 17.0545 20.2789 14.6667 17.3333 14.6667C14.3878 14.6667 12 17.0545 12 20C12 22.9455 14.3878 25.3333 17.3333 25.3333Z"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M17.3333 25.3333C20.2789 25.3333 22.6667 22.9455 22.6667 20C22.6667 17.0545 20.2789 14.6667 17.3333 14.6667C14.3878 14.6667 12 17.0545 12 20C12 22.9455 14.3878 25.3333 17.3333 25.3333Z"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M32.7999 28.76L31.7893 27.1413C31.6694 26.9496 31.5027 26.7914 31.3049 26.6818C31.1072 26.5722 30.8847 26.5146 30.6586 26.5146C30.4324 26.5146 30.21 26.5722 30.0122 26.6818C29.8144 26.7914 29.6478 26.9496 29.5279 27.1413L22.5013 38.4L19.6319 33.808C19.5121 33.6162 19.3454 33.4581 19.1476 33.3485C18.9498 33.2388 18.7274 33.1813 18.5013 33.1813C18.2751 33.1813 18.0527 33.2388 17.8549 33.3485C17.6571 33.4581 17.4904 33.6162 17.3706 33.808L9.33325 46.6667H22.6666"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M32.7999 28.76L31.7893 27.1413C31.6694 26.9496 31.5027 26.7914 31.3049 26.6818C31.1072 26.5722 30.8847 26.5146 30.6586 26.5146C30.4324 26.5146 30.21 26.5722 30.0122 26.6818C29.8144 26.7914 29.6478 26.9496 29.5279 27.1413L22.5013 38.4L19.6319 33.808C19.5121 33.6162 19.3454 33.4581 19.1476 33.3485C18.9498 33.2388 18.7274 33.1813 18.5013 33.1813C18.2751 33.1813 18.0527 33.2388 17.8549 33.3485C17.6571 33.4581 17.4904 33.6162 17.3706 33.808L9.33325 46.6667H22.6666"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M25.3333 62.6667H3.99992C3.29267 62.6667 2.6144 62.3857 2.1143 61.8856C1.6142 61.3855 1.33325 60.7072 1.33325 60V3.99999C1.33325 3.29275 1.6142 2.61447 2.1143 2.11438C2.6144 1.61428 3.29267 1.33333 3.99992 1.33333H39.4479C40.1551 1.33348 40.8333 1.61453 41.3333 2.11466L51.2186 12C51.7187 12.5 51.9998 13.1781 51.9999 13.8853V22.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M25.3333 62.6667H3.99992C3.29267 62.6667 2.6144 62.3857 2.1143 61.8856C1.6142 61.3855 1.33325 60.7072 1.33325 60V3.99999C1.33325 3.29275 1.6142 2.61447 2.1143 2.11438C2.6144 1.61428 3.29267 1.33333 3.99992 1.33333H39.4479C40.1551 1.33348 40.8333 1.61453 41.3333 2.11466L51.2186 12C51.7187 12.5 51.9998 13.1781 51.9999 13.8853V22.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 62.6667C55.5033 62.6667 62.6667 55.5032 62.6667 46.6667C62.6667 37.8301 55.5033 30.6667 46.6667 30.6667C37.8302 30.6667 30.6667 37.8301 30.6667 46.6667C30.6667 55.5032 37.8302 62.6667 46.6667 62.6667Z"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 62.6667C55.5033 62.6667 62.6667 55.5032 62.6667 46.6667C62.6667 37.8301 55.5033 30.6667 46.6667 30.6667C37.8302 30.6667 30.6667 37.8301 30.6667 46.6667C30.6667 55.5032 37.8302 62.6667 46.6667 62.6667Z"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 54.6667V38.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 54.6667V38.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 38.6667L40.6667 44.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 38.6667L40.6667 44.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 38.6667L52.6667 44.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        <path
                          d="M46.6667 38.6667L52.6667 44.6667"
                          stroke="#B0B6C1"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </g>
                    </svg>

                    <div className="flex text-sm text-gray-600">
                      <span className="inline-block mr-1 relative cursor-pointer bg-white rounded-md font-medium text-blue-800 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                        Browse
                      </span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        ref={fileRef}
                        {...getInputProps()}
                      />
                      or drag and drop an image to classify
                    </div>
                    <p className="text-xs text-gray-500">
                      Maximum file size is 10Mb
                    </p>
                  </div>
                </div>
              )}

              {/* <!--end of dropzone--> */}
              <div className="flex mt-6">
                <button
                  className="btn-primary has-icon"
                  onClick={submit}
                  disabled={loading || acceptedFiles.length === 0}
                >
                  {/* <!-- <svg className="w-3 h-3 mr-1" viewBox="0 0 7 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M6.29289 5.29289L1.70711 0.707107C1.07714 0.077142 0 0.523309 0 1.41421V10.5858C0 11.4767 1.07714 11.9229 1.70711 11.2929L6.29289 6.70711C6.68342 6.31658 6.68342 5.68342 6.29289 5.29289Z"
                  fill="white" fill-opacity="0.7" />
              </svg> --> */}
                  {loading && (
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  )}
                  Classify Image
                </button>
                <button className="btn-secondary ml-auto" onClick={reset}>
                  Reset
                </button>
              </div>
            </section>

            <section className="ui-output py-5 pl-5 pr-5 pl-2.5  w-1/2 ">
              <div>
                <h3 className="font-semibold text-blue-800 mb-4">Output</h3>
                {result.length > 0 && (
                  <ul className="flex flex-col justify-between -mt-1">
                    {result.map((r) => {
                      return (
                        <li className="flex items-center my-1">
                          <span className="pr-2 w-24">{r[0]}</span>
                          <div className="flex flex-1 items-center">
                            <div
                              className={klass(
                                {
                                  relative: r[1] < 0.3,
                                },
                                "flex h-8 px-4 rounded-lg bg-blue-800 p-1"
                              )}
                              style={{ width: `${r[1] * 100}%` }}
                            >
                              <span
                                className={klass(
                                  {
                                    "font-medium text-blue-800 absolute -right-1 transform translate-x-full":
                                      r[1] < 0.3,
                                    "text-white": r[1] >= 0.3,
                                  },
                                  "font-medium"
                                )}
                              >
                                {Number(r[1] * 100).toFixed(2)}%
                              </span>
                            </div>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            </section>
          </div>
        </div>
      </main>
    </Fragment>
  );
}
