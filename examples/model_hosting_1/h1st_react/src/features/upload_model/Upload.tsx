import React, { useState, useRef, useCallback, Fragment } from "react";
import klass from "classnames";
import { v4 } from "uuid";

import { useAuth0 } from "@auth0/auth0-react";
import { useAppSelector, useAppDispatch } from "app/hooks";
import {
  setShowModelPackingGuide,
  selectApplication,
  updateApplicationName,
  updateApplicationDescription,
  resetApplicationState,
  hideUploadForm,
  showMessage,
  addModel,
  MessageType,
  ModelTypes,
} from "./uploadSlice";
import { useDropzone } from "react-dropzone";
// import ModelInput from "features/upload_model/components/model_input";
// import ModelOutput from "features/upload_model/components/model_output";
import UploadService from "features/upload_model/service.upload";

import styles from "./Upload.module.css";
import SideContentPanel from "features/upload_model/components/guide";
import { getFullUrl } from "utils";
import {
  ActionType,
  DialogType,
  setGlobalDialogMessage,
} from "features/common/appSlice";
import { useHistory } from "react-router";
import { APP_PREFIX } from "config";

const axios = require("axios").default;

const BUTTON_STATES = {
  IDLE: "Save",
  UPLOADING: "Uploading...Please wait.",
  SAVING: "Saving...",
};

export default function UploadForm() {
  const { getAccessTokenSilently } = useAuth0();
  const fileRef = useRef<HTMLInputElement>(null);

  const [submitted, setSubmitted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [buttonState, setButtonState] = useState(BUTTON_STATES.IDLE);

  const history = useHistory();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length === 0) {
      dispatch(
        showMessage({
          title: "Missing file",
          message: "No file accepted",
          messageType: MessageType.ERROR,
        })
      );

      return;
    }

    // reset progress
    setProgress(0);
    setUploadedFile(null);
    setButtonState(BUTTON_STATES.UPLOADING);

    const token = await getAccessTokenSilently();
    const result = await UploadService.upload(
      getFullUrl("/api/upload/"),
      { file: acceptedFiles[0] },
      (event) => {
        const prog = Math.round((100 * event.loaded) / event.total);
        setProgress(prog);
      },
      token
    );

    if (result.data.status === "OK") {
      // set the uploaded file here
      setUploadedFile(result.data.id);
    }

    setButtonState(BUTTON_STATES.IDLE);
  }, []);

  const { acceptedFiles, getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: [
      "application/zip",
      "application/octet-stream",
      "application/x-zip-compressed",
      "multipart/x-zip",
    ],
  });
  const applicationInfo = useAppSelector(selectApplication);
  const dispatch = useAppDispatch();

  const files = acceptedFiles.map((file) => (
    // @ts-ignore
    <li key={file.path}>
      {/* @ts-ignore */}
      {file.path}
    </li>
  ));

  const updateAppName = (value: string) => {
    dispatch(updateApplicationName(value));
  };

  const updateAppDescription = (value: string) => {
    dispatch(updateApplicationDescription(value));
  };

  // const addNewModelInput = () => {
  //   dispatch(addModelInput({ type: "string", name: "", id: v4() }));
  // };

  const cancel = () => {
    UploadService.cancelRequest();
    dispatch(resetApplicationState());
    dispatch(hideUploadForm());
  };

  const submit = async () => {
    setSubmitted(true);
    setButtonState(BUTTON_STATES.SAVING);

    const token = await getAccessTokenSilently();
    const { name, description, input: rawInput, output } = applicationInfo;

    const input = rawInput.filter((i) => i.name.trim() !== "");
    const type = ModelTypes.TENSORFLOW;

    try {
      const response = await axios.post(
        getFullUrl("/api/upload/"),
        {
          name,
          description,
          type,
          input,
          output,
          uploadedFile,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.status === "OK") {
        dispatch(addModel(response.data.result));

        dispatch(
          showMessage({
            title: "Success",
            message: `${name} has been uploaded successfully`,
            messageType: MessageType.SUCCESS,
          })
        );

        setTimeout(() => {
          setSubmitted(false);
          dispatch(resetApplicationState());
          dispatch(hideUploadForm());

          history.push(
            `${APP_PREFIX}/application/${response.data.result.model_id}/execute`
          );
        }, 1000);
      } else {
        dispatch(
          setGlobalDialogMessage({
            type: DialogType.ERROR,
            action: ActionType.OK,
            title: "Error",
            message:
              "An error occured when trying to save model. Please try again.",
          })
        );
      }
    } catch (ex) {
      console.log(ex.response.data);
      dispatch(
        setGlobalDialogMessage({
          type: DialogType.ERROR,
          action: ActionType.OK,
          title: "Error",
          message:
            "An error occured when trying to save model. Please try again.",
        })
      );
    } finally {
      setButtonState(BUTTON_STATES.IDLE);
    }
  };

  const showModelGuide = () => {
    dispatch(setShowModelPackingGuide(true));
  };

  // const modelInputs = applicationInfo.input.map((input, index) => (
  //   <li>
  //     <ModelInput
  //       key={input.id}
  //       id={input.id}
  //       name={input.name}
  //       index={index}
  //     />
  //   </li>
  // ));

  return (
    <Fragment>
      <SideContentPanel title="Model Packaging Guide">
        <div className="text-sm text-gray-900 p-6">
          <h3 className="text-xl">Overall package structure</h3>

          <p className="my-4">
            Upload format we are looking for is a zip package that contain:
            <ol className="list-decimal list-inside my-2">
              <li>Tensorflow2 SavedModel</li>
              <li>
                Config file:{" "}
                <span className="text-yellow-600 font-mono">model-io.json</span>
              </li>
            </ol>
          </p>

          <p className="my-4">
            An unzipped sample structure for the package would be
            <pre className="bg-gray-200 p-4 my-4 font-mono font-xs">
              {` __ saved_model_folder
|   |__ assets
|   |__ variables
|   |__ saved_model.pb
|__ model-io.json`}
            </pre>
            <ol>
              <li>
                <h3 className="text-xl">1. Tensorflow2 SaveModel</h3>
                <p className="my-4">
                  We support{" "}
                  <a
                    href="https://www.tensorflow.org/guide/saved_model"
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600"
                  >
                    Tensorflow2 SavedModel standard
                  </a>
                  <br />
                  <span className="bg-gray-200 font-mono inline-block px-2 rounded-sm text-xs">
                    tf.saved_model.save(model, path_to_dir)
                  </span>{" "}
                  or{" "}
                  <span className="bg-gray-200 font-mono inline-block px-2 rounded-sm text-xs">
                    model.save()
                  </span>
                </p>
                <p className="my-4">
                  If you saved your model in different formats, please take a
                  look at{" "}
                  <a
                    href="https://www.tensorflow.org/guide/keras/save_and_serialize"
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600"
                  >
                    this document
                  </a>{" "}
                  from Tensorflow to save it in SaveModel format.
                </p>
              </li>

              <li>
                <h3 className="text-xl">
                  2. Config file:{" "}
                  <span className="font-mono text-lg text-yellow-600">
                    model-io.json
                  </span>
                </h3>
                <p className="my-4">
                  In this file you can specify the input-mapping and
                  output-mapping for the model as well as input-shape or
                  input-scaling. If you don’t want to run these preprocessing
                  and postprocessing, you don’t need to provide them.
                </p>
                <p className="my-4">
                  <ul className="list-disc pl-4">
                    <li className="my-4">
                      <span className="text-yellow-600 font-mono">
                        input-image-shape
                      </span>
                      : an input-shape array (integers) for width and height ,
                      not including the batch size. Example:
                      <pre className="bg-gray-200 p-4 my-4 font-mono font-xs">
                        "input-image-shape": [224, 224]
                      </pre>
                    </li>
                    <li className="my-4">
                      <span className="text-yellow-600 font-mono">
                        input-scaling
                      </span>
                      : If you want to run min_max scaling at runtime, please
                      provide input-min, input-max, target-min, target-max.
                      Example:
                      <pre className="bg-gray-200 p-4 my-4 font-mono font-xs">
                        {`"input-scaling": {
    "input-min":[0, 0, 0], "input-max":[255, 255, 255],
    "target-min":[-1, -1, -1], "target-max":[1, 1, 1],
}`}
                      </pre>
                    </li>
                    <li className="my-4">
                      <span className="text-yellow-600 font-mono">
                        output-class-limit
                      </span>
                      : the maximum number of classes to be displayed/returned.
                    </li>
                    <li className="my-4">
                      <span className="text-yellow-600 font-mono">
                        output-mapping
                      </span>
                      : an array mapping for the output.
                    </li>
                  </ul>
                </p>
              </li>
            </ol>
          </p>
          <p className="my-4">
            An example model-io.json file would be the following
            <pre className="bg-gray-200 p-4 my-4 font-mono font-xs">
              {`{
    "input-image-shape": [224, 224], 
    "input-scaling": {
        "input-mean":[123.675, 116.28, 103.53],
        "input-std":[58.395, 57.12, 57.375]
    },
    "output-mapping": [ "tench", "goldfish", "great white" ... ]
}`}
            </pre>
          </p>
        </div>
      </SideContentPanel>

      <div className="py-6 px-8 shadow rounded bg-white">
        <div className="space-y-8 divide-y divide-gray-200">
          <div className="space-y-8 divide-y divide-gray-200">
            <div>
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Upload a model
                </h3>
                <p className="mt-1 text-sm text-gray-500 mb-4">
                  Upload a Tensorflow model from your local drive.
                </p>

                <div className="px-4 py-3 bg-blue-50 border rounded-lg border-blue-200">
                  <p>
                    We currently support{" "}
                    <span className="text-blue-800">ImageClassification</span>.
                    New model type support is coming soon.
                  </p>
                  <p>
                    <a
                      // onClick={showModelGuide}
                      href="https://docs.google.com/document/d/e/2PACX-1vQmaYlLeSSX0iE0XjomOq4_IbUtdYaieD3kuD2vKvCRZ1GzerxdBBEZjefifiiQUid3zHsxILTressJ/pub"
                      className="flex items-centerblock mt-1 font-bold"
                      target="_blank"
                      rel="noreferrer"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      How to prepare your Image Classification model
                    </a>
                  </p>
                </div>

                {/* <label
                  htmlFor="model_type"
                  className="block text-sm font-medium text-gray-700"
                >
                  Model Type
                </label> */}
              </div>

              <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-6">
                  <div
                    {...getRootProps({
                      className:
                        "hover:border-blue-500 dropzone mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-gray-300 border-dashed rounded-md",
                    })}
                  >
                    <div className="space-y-1 text-center relative">
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
                        <span className="text-blue-600">Select file</span> or
                        drag and drop a file here to upload (limit: 600MB)
                      </p>
                      {acceptedFiles.length > 0 && (
                        <aside>
                          <ul>{files}</ul>
                          <span
                            className={klass(
                              styles["progress-bar"],
                              "w-64 h-2 bottom-2 left-0 bg-blue-200 m-auto"
                            )}
                          >
                            <span
                              className={styles["progress-bar-content"]}
                              style={{
                                display: "block",
                                transform: `scaleX(${Number(
                                  progress / 100
                                ).toFixed(2)})`,
                              }}
                            ></span>
                          </span>
                        </aside>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="space-y-8 divide-y divide-gray-200 pt-4">
            <div>
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Model Information
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Provide information and upload your model file
                </p>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-4">
                  <label
                    htmlFor="model_name"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Model Name (required)
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <input
                      type="text"
                      name="model_name"
                      id="model_name"
                      value={applicationInfo.name}
                      onChange={(e) => updateAppName(e.target.value)}
                      className={klass(
                        "flex-1 focus:ring-blue-500 focus:border-blue-500 block w-full min-w-0 rounded sm:text-sm border-gray-300",
                        {
                          "border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500":
                            submitted && !applicationInfo.name,
                        }
                      )}
                    />
                  </div>
                </div>

                <div className="sm:col-span-6">
                  <label
                    htmlFor="about"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Description (optional)
                  </label>
                  <div className="mt-1">
                    <textarea
                      id="description"
                      name="description"
                      rows={3}
                      value={applicationInfo.description}
                      onChange={(e) => updateAppDescription(e.target.value)}
                      className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-5">
            <div className="flex justify-start">
              <button
                type="button"
                className="disabled:pointer-events-none disabled:opacity-50 mr-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center"
                disabled={
                  !applicationInfo.name || // no application name
                  !fileRef || // no file upload ref
                  !uploadedFile || // there is no uploaded file
                  buttonState !== BUTTON_STATES.IDLE // there is something going one
                }
                onClick={submit}
              >
                {buttonState === BUTTON_STATES.SAVING && (
                  <span className="flex h-2 w-2 relative mr-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-200 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-400"></span>
                  </span>
                )}
                {buttonState}
              </button>

              <button
                type="button"
                className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                onClick={cancel}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </Fragment>
  );
}
