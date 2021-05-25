import React, { FunctionComponent } from "react";
import { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { XIcon } from "@heroicons/react/outline";

import { useAppDispatch, useAppSelector } from "app/hooks";
import {
  setShowModelPackingGuide,
  selectApplication,
} from "features/upload_model/uploadSlice";

export interface GuildPanelProps {
  title: string;
  children: any;
}

const ModelPackingGuide: FunctionComponent<GuildPanelProps> = (props) => {
  const dispatch = useAppDispatch();

  // const setOpen = () => {
  //   dispatch(setShowModelPackingGuide(true));
  // };

  const setClose = () => {
    dispatch(setShowModelPackingGuide(false));
  };

  const { showGuide: open } = useAppSelector(selectApplication);

  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog
        as="div"
        static
        className="fixed inset-0 overflow-hidden z-10 bg-gray-600 bg-opacity-50"
        open={open}
        onClose={setClose}
      >
        <div className="absolute inset-0 overflow-hidden">
          <Dialog.Overlay className="absolute inset-0" />

          <div className="fixed inset-y-0 right-0 pl-10 max-w-full flex sm:pl-16">
            <Transition.Child
              as={Fragment}
              enter="transform transition ease-in-out duration-500 sm:duration-700"
              enterFrom="translate-x-full"
              enterTo="translate-x-0"
              leave="transform transition ease-in-out duration-500 sm:duration-700"
              leaveFrom="translate-x-0"
              leaveTo="translate-x-full"
            >
              <div className="w-screen max-w-lg">
                <div className="h-full flex flex-col py-6 bg-white shadow-xl overflow-y-scroll">
                  <div className="px-4 sm:px-6">
                    <div className="flex items-start justify-between">
                      {/* <Dialog.Title className="text-2xl font-medium text-gray-900">
                        
                      </Dialog.Title> */}
                      <h2
                        className="text-lg font-medium text-gray-900"
                        id="slide-over-title"
                      >
                        {props.title}
                      </h2>
                      <div className="ml-3 h-7 flex items-center">
                        <button
                          className="bg-white rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-900"
                          onClick={setClose}
                        >
                          <span className="sr-only">Close panel</span>
                          <XIcon className="h-6 w-6" aria-hidden="true" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="mt-6 relative flex-1 px-4 sm:px-6">
                    {/* Replace with your content */}
                    <div className="absolute inset-0 px-4 sm:px-6">
                      {props.children}
                    </div>
                    {/* /End replace */}
                  </div>
                </div>
              </div>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};

export default ModelPackingGuide;
