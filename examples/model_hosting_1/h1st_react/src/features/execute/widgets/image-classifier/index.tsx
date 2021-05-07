import React, { useState, useRef, useCallback } from "react";
import { AIModel } from "features/upload_model/uploadSlice";
import UploadService from "features/upload_model/service.upload";

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

  const onDrop = useCallback((acceptedFiles) => {
    var reader = new FileReader();

    reader.onload = function (e) {
      // previewImgEl?.current?.src = e.target?.result;

      // previewImgEl.current?.src = e.target?.result;
      // console.log(previewImgEl);
      // console.log(e.target?.result);
      // @ts-ignore
      setPreviewSrc(e.target.result);
    };

    reader.readAsDataURL(acceptedFiles[0]);
  }, []);

  const { acceptedFiles, getRootProps, getInputProps } = useDropzone({
    onDrop,
  });

  if (!model) {
    return null;
  }

  // const { name, type } = JSON.parse(model.input)[0];
  // console.log(JSON.parse(intput));

  // const name = "input";
  // const type = "image";

  // if (!name || !type) {
  //   return <p>Invalid input</p>;
  // }

  const submit = async () => {
    const res = await UploadService.upload(
      `/api/app/${model.model_id}/execute/img_classifer/`,
      { file: acceptedFiles[0], model_id: model.model_id },
      (event) => {
        const prog = Math.round((100 * event.loaded) / event.total);
        console.log(prog);
        setProgress(prog);
      }
    );

    console.log(res);

    if (res.data.status === "OK") {
      setResult(res.data.result.slice(0, 3));
      // set the uploaded file here
      // setUploadedFile(result.data.id);
    }
  };

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
                      "hover:border-indigo-500 dropzone mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-gray-300 border-dashed rounded-md",
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
                        className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
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
            className="mt-3 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
            onClick={submit}
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
}
