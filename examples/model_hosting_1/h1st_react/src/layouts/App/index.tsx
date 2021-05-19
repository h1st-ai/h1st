import React, { Fragment, useState } from "react";
import { Disclosure, Menu, Transition } from "@headlessui/react";
import { BellIcon, MenuIcon, XIcon } from "@heroicons/react/outline";

import StatusMessage from "components/StatusMessage";
import Logo from "components/logo";

import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router-dom";
import { APP_PREFIX } from "config";
import GlobalMessageDialog from "components/global-dialog";
import { showMessage } from "features/upload_model/uploadSlice";

const navigation = [{ label: "Your Models", url: `/${APP_PREFIX}/dashboard` }];
const profile = ["Sign out"];

function classNames(...classes: any) {
  return classes.filter(Boolean).join(" ");
}

export default function App(props: any) {
  const { logout, user, isAuthenticated, isLoading, loginWithRedirect } =
    useAuth0();

  const [showRoadmap, setShowRoadmap] = useState(false);

  if (isLoading) {
    return <div>Loading ...</div>;
  }

  if (!isAuthenticated) {
    loginWithRedirect({
      appState: { returnTo: `/${APP_PREFIX}/upload` },
    });

    return null;
  }

  return (
    <Fragment>
      <div className="min-h-screen">
        {showRoadmap && (
          <div
            className="coming-soon-dialog fixed z-10 inset-0 overflow-y-auto"
            aria-labelledby="modal-title"
            role="dialog"
            aria-modal="true"
          >
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              {/* <!--
        Background overlay, show/hide based on modal state.
  
        Entering: "ease-out duration-300"
          From: "opacity-0"
          To: "opacity-100"
        Leaving: "ease-in duration-200"
          From: "opacity-100"
          To: "opacity-0"
      --> */}
              <div
                className="fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity"
                aria-hidden="true"
              ></div>

              {/* <!-- This element is to trick the browser into centering the modal contents. --> */}
              <span
                className="hidden sm:inline-block sm:align-middle sm:h-screen"
                aria-hidden="true"
              >
                &#8203;
              </span>

              {/* <!--
        Modal panel, show/hide based on modal state.
  
        Entering: "ease-out duration-300"
          From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          To: "opacity-100 translate-y-0 sm:scale-100"
        Leaving: "ease-in duration-200"
          From: "opacity-100 translate-y-0 sm:scale-100"
          To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
      --> */}
              <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-sm sm:w-full sm:p-6">
                <div>
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                    {/* <!-- Heroicon name: outline/check --> */}
                    <svg
                      className="h-6 w-6 text-green-600"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <div className="mt-3 text-center sm:mt-5">
                    <h3
                      className="text-lg leading-6 font-medium text-gray-900"
                      id="modal-title"
                    >
                      Coming soon
                    </h3>
                    <div className="mt-2 text-left">
                      <div className="text-sm text-gray-600">
                        <ul>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            NLP: Text Classification
                          </li>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            NLP: Translation
                          </li>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            NLP: Text Summary
                          </li>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            Image Captioning
                          </li>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            Time Series Anomaly Detection
                          </li>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            Model Inference API
                          </li>
                          <li className="flex items-center">
                            <svg className="w-4 h-4 mr-1.5 text-green-600">
                              <use xlinkHref="#icon-checked" />
                            </svg>
                            and more ...
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-5 sm:mt-6">
                  <button
                    type="button"
                    className="inline-flex justify-center w-full rounded-md border border-transparent shadow-sm px-4 py-2 bg-slate-200 text-base font-medium text-gray-700 font-semibold tracking-wide hover:bg-slate-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm"
                    onClick={() => setShowRoadmap(false)}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        <GlobalMessageDialog />
        <StatusMessage />
        <Disclosure as="nav" className="bg-gray-800">
          {({ open }) => (
            <>
              <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Link to={`/${APP_PREFIX}`}>
                        <Logo />
                      </Link>
                    </div>
                    <div className="hidden md:block">
                      <div className="ml-10 flex items-baseline space-x-4">
                        {navigation.map((item, itemIdx) =>
                          itemIdx === 0 ? (
                            <Fragment key={item.label}>
                              {/* Current: "bg-gray-900 text-white", Default: "text-gray-300 hover:bg-gray-700 hover:text-white" */}
                              <Link
                                to={item.url}
                                className="bg-gray-900 text-white px-3 py-2 rounded-md text-sm font-medium"
                              >
                                {item.label}
                              </Link>
                            </Fragment>
                          ) : (
                            <Link
                              to={item.url}
                              className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                            >
                              {item.label}
                            </Link>
                          )
                        )}

                        <button
                          onClick={() => setShowRoadmap(true)}
                          className="text-white bg-green-700 px-4 py-2 rounded-full text-sm font-semibold tracking-wide"
                        >
                          Roadmap
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="hidden md:block">
                    <div className="ml-4 flex items-center md:ml-6">
                      <button className="bg-gray-800 p-1 rounded-full text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                        <span className="sr-only">View notifications</span>
                        <BellIcon className="h-6 w-6" aria-hidden="true" />
                      </button>

                      {/* Profile dropdown */}
                      <Menu as="div" className="ml-3 relative">
                        {({ open }) => (
                          <>
                            <div>
                              <Menu.Button className="max-w-xs bg-gray-800 rounded-full flex items-center text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                                <span className="sr-only">Open user menu</span>
                                <img
                                  className="h-8 w-8 rounded-full"
                                  src={user?.picture}
                                  alt=""
                                />
                              </Menu.Button>
                            </div>
                            <Transition
                              show={open}
                              as={Fragment}
                              enter="transition ease-out duration-100"
                              enterFrom="transform opacity-0 scale-95"
                              enterTo="transform opacity-100 scale-100"
                              leave="transition ease-in duration-75"
                              leaveFrom="transform opacity-100 scale-100"
                              leaveTo="transform opacity-0 scale-95"
                            >
                              <Menu.Items
                                static
                                className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
                              >
                                {profile.map((item) => (
                                  <Menu.Item
                                    key={item}
                                    onClick={() =>
                                      logout({
                                        returnTo: `${window.location.origin}/${APP_PREFIX}`,
                                      })
                                    }
                                  >
                                    {({ active }) => (
                                      <a
                                        href="#logout"
                                        className={classNames(
                                          active ? "bg-gray-100" : "",
                                          "block px-4 py-2 text-sm text-gray-700"
                                        )}
                                      >
                                        {item}
                                      </a>
                                    )}
                                  </Menu.Item>
                                ))}
                              </Menu.Items>
                            </Transition>
                          </>
                        )}
                      </Menu>
                    </div>
                  </div>
                  <div className="-mr-2 flex md:hidden">
                    {/* Mobile menu button */}
                    <Disclosure.Button className="bg-gray-800 inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                      <span className="sr-only">Open main menu</span>
                      {open ? (
                        <XIcon className="block h-6 w-6" aria-hidden="true" />
                      ) : (
                        <MenuIcon
                          className="block h-6 w-6"
                          aria-hidden="true"
                        />
                      )}
                    </Disclosure.Button>
                  </div>
                </div>
              </div>

              <Disclosure.Panel className="md:hidden">
                <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                  {navigation.map((item, itemIdx) =>
                    itemIdx === 0 ? (
                      <Fragment key={item.label}>
                        {/* Current: "bg-gray-900 text-white", Default: "text-gray-300 hover:bg-gray-700 hover:text-white" */}
                        <Link
                          to={item.url}
                          className="bg-gray-900 text-white block px-3 py-2 rounded-md text-base font-medium"
                        >
                          {item.label}
                        </Link>
                      </Fragment>
                    ) : (
                      <Link
                        to={item.url}
                        className="text-gray-300 hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                      >
                        {item.label}
                      </Link>
                    )
                  )}

                  <button
                    onClick={() => setShowRoadmap(true)}
                    className="text-white bg-green-700 px-4 py-2 rounded-full text-sm font-semibold tracking-wide"
                  >
                    Roadmap
                  </button>
                </div>
                <div className="pt-4 pb-3 border-t border-gray-700">
                  <div className="flex items-center px-5">
                    <div className="flex-shrink-0">
                      <img
                        className="h-10 w-10 rounded-full"
                        src={user?.picture}
                        alt={user?.name}
                      />
                    </div>
                    <div className="ml-3">
                      <div className="text-base font-medium leading-none text-white">
                        {user?.name}
                      </div>
                      <div className="text-sm font-medium leading-none text-gray-400">
                        {user?.nickname}
                      </div>
                    </div>
                    <button className="ml-auto bg-gray-800 flex-shrink-0 p-1 rounded-full text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                      <span className="sr-only">View notifications</span>
                      <BellIcon className="h-6 w-6" aria-hidden="true" />
                    </button>
                  </div>
                  <div className="mt-3 px-2 space-y-1">
                    {profile.map((item) => (
                      <a
                        key={item}
                        href="#444"
                        className="block px-3 py-2 rounded-md text-base font-medium text-gray-400 hover:text-white hover:bg-gray-700"
                        onClick={() =>
                          logout({
                            returnTo: `${window.location.origin}/${APP_PREFIX}`,
                          })
                        }
                      >
                        {item}
                      </a>
                    ))}
                  </div>
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        {/* Replace with your content */}
        {props.children}
        {/* /End replace */}
      </div>
    </Fragment>
  );
}
