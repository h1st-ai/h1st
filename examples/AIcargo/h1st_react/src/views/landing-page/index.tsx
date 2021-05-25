import React, { Fragment, useState } from "react";

import Logo from "./img/logo.svg";
import LogoFooter from "./img/logo-footer.svg";
import Illus1 from "./img/illus-1.svg";
import Illus2 from "./img/illus-2.svg";
import Illus3 from "./img/illus-3.svg";
import Illus4 from "./img/illus-4.svg";
import { useHistory } from "react-router";
import { APP_PREFIX } from "config";
import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router-dom";

export default function LandingPage(props: any) {
  const history = useHistory();
  const { loginWithRedirect, loginWithPopup, isAuthenticated, isLoading } =
    useAuth0();

  return (
    <Fragment>
      <main className="bg-white-200 text-sm min-h-screen">
        <div className="bg-blue-900 py-4 lg:py-6">
          <div className="mx-auto max-w-5xl p-5 text-center lg:text-left">
            <nav className="flex">
              <img
                src={Logo}
                className="flex"
                alt="AICargo - Bring your models to life"
              />
              {!isLoading && !isAuthenticated && (
                <ul className="mr-0 ml-auto flex">
                  <li className="ml-2">
                    <button
                      className="outline-none px-2 py-3 text-white font-semibold tracking-wide text-base hover:text-blue-200"
                      onClick={() =>
                        loginWithRedirect({
                          appState: { returnTo: `/${APP_PREFIX}/dashboard` },
                        })
                      }
                    >
                      Sign in
                    </button>
                  </li>
                  <li className="ml-2">
                    <button
                      className="outline-none px-2 py-3 text-white font-semibold tracking-wide text-base hover:text-blue-200"
                      onClick={() => loginWithPopup()}
                    >
                      Sign up
                    </button>
                  </li>
                </ul>
              )}

              {!isLoading && isAuthenticated && (
                <ul className="mr-0 ml-auto flex">
                  <li className="ml-2">
                    <Link
                      className="outline-none px-2 py-3 text-white font-semibold tracking-wide text-base hover:text-blue-200"
                      to={`/${APP_PREFIX}/dashboard`}
                    >
                      My Models
                    </Link>
                  </li>
                </ul>
              )}
            </nav>
            <div className="lg:flex block items-center md:text-center lg:text-left lg:pt-10 pt-4">
              <div className="lg:w-1/2 text-center lg:text-left lg:px-5">
                <h1 className="text-white text-2xl lg:text-4xl font-bold tracking-wide">
                  Bring your models to life
                </h1>
                <div className="flex items-center my-4">
                  <button
                    type="button"
                    className="inline-flex mr-4 lg:ml-0 btn-primary dark-bg hero has-icon"
                    onClick={() => history.push(`/${APP_PREFIX}/upload`)}
                  >
                    <svg
                      className="icon"
                      width="20"
                      height="24"
                      viewBox="0 0 20 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M0.499972 23.5C0.499972 23.6326 0.55265 23.7598 0.646419 23.8536C0.740187 23.9473 0.867364 24 0.999972 24H19.5C19.6326 24 19.7598 23.9473 19.8535 23.8536C19.9473 23.7598 20 23.6326 20 23.5C20.0181 22.7371 19.7375 21.9973 19.218 21.4384C18.6985 20.8795 17.9811 20.5456 17.219 20.508C17.1609 20.504 17.106 20.4798 17.0638 20.4396C17.0216 20.3995 16.9948 20.3458 16.988 20.288C16.8551 19.742 16.5312 19.2615 16.0749 18.9336C15.6185 18.6056 15.0599 18.4518 14.5 18.5H13.7C13.6471 18.5001 13.5957 18.5169 13.553 18.548C13.5102 18.579 13.4784 18.6228 13.462 18.673C12.9824 19.9241 12.2583 21.067 11.332 22.035C11.1919 22.1817 11.0235 22.2985 10.837 22.3783C10.6506 22.4581 10.4498 22.4993 10.247 22.4993C10.0441 22.4993 9.84339 22.4581 9.6569 22.3783C9.47041 22.2985 9.30204 22.1817 9.16197 22.035C8.23565 21.067 7.51155 19.9241 7.03197 18.673C7.01589 18.6237 6.98495 18.5807 6.94342 18.5497C6.90188 18.5187 6.85177 18.5014 6.79997 18.5H5.99997C5.44026 18.4565 4.88335 18.6137 4.42907 18.9436C3.9748 19.2734 3.65286 19.7543 3.52097 20.3C3.51225 20.3563 3.48463 20.408 3.44265 20.4465C3.40066 20.485 3.34682 20.5081 3.28997 20.512C2.52701 20.5476 1.80817 20.88 1.2869 21.4382C0.765629 21.9965 0.483226 22.7364 0.499972 23.5Z"
                        fill="#B5C2F0"
                      />
                      <path
                        d="M10.25 15.478C9.99123 15.4698 9.73359 15.515 9.49306 15.6107C9.25254 15.7064 9.03427 15.8505 8.85184 16.0342C8.66941 16.2178 8.52672 16.4371 8.43263 16.6782C8.33855 16.9194 8.29509 17.1773 8.30496 17.436C8.30496 18.667 9.57296 20.236 10.062 20.792C10.0854 20.8188 10.1143 20.8402 10.1468 20.8549C10.1792 20.8696 10.2144 20.8772 10.25 20.8772C10.2856 20.8772 10.3207 20.8696 10.3532 20.8549C10.3856 20.8402 10.4145 20.8188 10.438 20.792C10.926 20.235 12.195 18.668 12.195 17.436C12.2048 17.1773 12.1614 16.9194 12.0673 16.6782C11.9732 16.4371 11.8305 16.2178 11.6481 16.0342C11.4656 15.8505 11.2474 15.7064 11.0069 15.6107C10.7663 15.515 10.5087 15.4698 10.25 15.478Z"
                        fill="#B5C2F0"
                      />
                      <path
                        d="M12.646 2.492C12.2446 2.21368 11.8189 1.97235 11.374 1.771C11.3243 1.74688 11.2841 1.70702 11.2595 1.65764C11.2349 1.60826 11.2273 1.55213 11.238 1.498C11.2472 1.45123 11.2519 1.40368 11.252 1.356V1C11.252 0.734784 11.1466 0.48043 10.9591 0.292893C10.7715 0.105357 10.5172 0 10.252 0C9.98674 0 9.73239 0.105357 9.54485 0.292893C9.35732 0.48043 9.25196 0.734784 9.25196 1V1.356C9.25201 1.40368 9.2567 1.45123 9.26596 1.498C9.27659 1.55213 9.26901 1.60826 9.24441 1.65764C9.21982 1.70702 9.17957 1.74688 9.12996 1.771C8.68521 1.9721 8.25977 2.21344 7.85896 2.492C7.43451 2.85753 7.104 3.31959 6.89518 3.83936C6.68637 4.35913 6.60536 4.92142 6.65896 5.479V5.489L7.78696 10.619C7.79955 10.6775 7.79085 10.7385 7.76243 10.7911C7.73402 10.8437 7.68775 10.8845 7.63196 10.906L7.47596 10.966C7.03906 11.1349 6.66534 11.4352 6.40634 11.8255C6.14735 12.2158 6.01584 12.6768 6.02996 13.145C6.10996 15.919 6.11696 15.72 8.57296 14.16H11.923L13.551 15.195C13.6354 15.2486 13.7325 15.2788 13.8325 15.2827C13.9324 15.2865 14.0316 15.2638 14.1199 15.2168C14.2082 15.1699 14.2825 15.1004 14.3352 15.0154C14.3879 14.9304 14.4171 14.833 14.42 14.733L14.466 13.146C14.4796 12.6772 14.3473 12.2158 14.0873 11.8255C13.8274 11.4352 13.4527 11.1352 13.015 10.967L12.859 10.907C12.8032 10.8855 12.7571 10.8447 12.7288 10.792C12.7006 10.7394 12.6921 10.6783 12.705 10.62C12.774 10.306 13.756 5.793 13.84 5.48C13.8944 4.92276 13.8145 4.36058 13.6067 3.84065C13.3989 3.32073 13.0695 2.85824 12.646 2.492ZM10.252 6.68C9.99737 6.68 9.74851 6.60449 9.53684 6.46303C9.32517 6.32157 9.16021 6.12051 9.06283 5.88528C8.96545 5.65006 8.94002 5.39123 8.98976 5.14155C9.0395 4.89187 9.16218 4.66255 9.34227 4.4826C9.52236 4.30265 9.75177 4.18015 10.0015 4.13061C10.2512 4.08106 10.51 4.10669 10.7452 4.20425C10.9803 4.30182 11.1813 4.46693 11.3225 4.67871C11.4638 4.89049 11.5392 5.13941 11.539 5.394C11.539 5.56296 11.5057 5.73027 11.441 5.88636C11.3763 6.04245 11.2815 6.18426 11.1619 6.30369C11.0424 6.42312 10.9005 6.51783 10.7444 6.5824C10.5883 6.64696 10.4209 6.68013 10.252 6.68Z"
                        fill="#B5C2F0"
                      />
                    </svg>
                    Upload your models
                  </button>
                </div>
              </div>
              <div className="lg:w-1/2 pl-5">
                <img src={Illus1} alt="AICargo - Bring your models to life" />
              </div>
            </div>
          </div>
        </div>
        <section className="mx-auto max-w-4xl py-10">
          <h1 className="flex items-center text-slate-700 text-xl text-center max-w-2xl lg:text-3xl mx-auto font-bold tracking-wide">
            <span className="mr-1 ml-auto">Built on</span>{" "}
            <a
              className="text-blue-800 hover:text-blue-600 "
              target="_blank"
              href="https://github.com/h1st-ai/h1st"
              rel="noreferrer"
            >
              H1st AI App Framework{" "}
            </a>
            <a
              className="inline-flex items-center text-base px-2 py-1.5 ml-2 mr-auto rounded-lg border border-gray-200 text-gray-600 hover:text-blue-700 hover:bg-gray-100"
              href="https://github.com/h1st-ai/h1st"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 mr-0"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              Star on Github
            </a>
          </h1>
          <h1 className="block text-slate-700 text-xl lg:text-3xl mx-auto font-bold tracking-wide text-center max-w-2xl">
            Powered by{" "}
            <a
              className="text-blue-800 hover:text-blue-600"
              target="_blank"
              href="https://www.aitomatic.com/products"
              rel="noreferrer"
            >
              Aitomatic H1stFlow Cloud Server
            </a>
          </h1>
          <div className="mt-2 lg:mt-10">
            <div className="lg:flex items-center py-5">
              <div className="lg:w-1/2 p-5">
                <img
                  src={Illus2}
                  className="mx-auto"
                  alt="Host your models for free"
                />
              </div>
              <div className="lg:w-1/2 p-5 ">
                <h2 className="text-blue-800 mb-5 font-semibold text-2xl">
                  Host your models for free
                </h2>
                <p className="text-gray-600 text-lg font-medium">
                  Just a few clicks to give your models a new home on the
                  Aitomatic cloud.
                </p>
              </div>
            </div>

            <div className="lg:flex items-center py-5">
              <div className="lg:w-1/2 p-5">
                <img
                  src={Illus3}
                  className="mx-auto"
                  alt="Interact with your models"
                />
              </div>
              <div className="lg:w-1/2 p-5 order-first ">
                <h2 className="text-blue-800 mb-5 font-semibold text-2xl">
                  Interact with your models
                </h2>
                <p className="text-gray-600 text-lg font-medium">
                  We provide convenient ready-made UI widgets for different
                  model types.
                </p>
              </div>
            </div>

            <div className="lg:flex items-center py-5">
              <div className="lg:w-1/2 p-5">
                <img
                  src={Illus4}
                  className="mx-auto"
                  alt="Share you models with the world"
                />
              </div>
              <div className="lg:w-1/2 p-5 ">
                <h2 className="text-blue-800 mb-5 font-semibold text-2xl">
                  Share you models with the world
                </h2>
                <p className="text-gray-600 text-lg font-medium">
                  Show them to your friends and family, integrate them into apps
                  with your co-workers, or link them to your porfolio.
                </p>
              </div>
            </div>
          </div>
        </section>
        <div className="text-center mb-5">
          <button
            type="button"
            className="inline-flex mb-12 lg:ml-0 btn-primary dark-bg hero has-icon"
            onClick={() => history.push(`/${APP_PREFIX}/upload`)}
          >
            <svg
              className="icon"
              width="20"
              height="24"
              viewBox="0 0 20 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M0.499972 23.5C0.499972 23.6326 0.55265 23.7598 0.646419 23.8536C0.740187 23.9473 0.867364 24 0.999972 24H19.5C19.6326 24 19.7598 23.9473 19.8535 23.8536C19.9473 23.7598 20 23.6326 20 23.5C20.0181 22.7371 19.7375 21.9973 19.218 21.4384C18.6985 20.8795 17.9811 20.5456 17.219 20.508C17.1609 20.504 17.106 20.4798 17.0638 20.4396C17.0216 20.3995 16.9948 20.3458 16.988 20.288C16.8551 19.742 16.5312 19.2615 16.0749 18.9336C15.6185 18.6056 15.0599 18.4518 14.5 18.5H13.7C13.6471 18.5001 13.5957 18.5169 13.553 18.548C13.5102 18.579 13.4784 18.6228 13.462 18.673C12.9824 19.9241 12.2583 21.067 11.332 22.035C11.1919 22.1817 11.0235 22.2985 10.837 22.3783C10.6506 22.4581 10.4498 22.4993 10.247 22.4993C10.0441 22.4993 9.84339 22.4581 9.6569 22.3783C9.47041 22.2985 9.30204 22.1817 9.16197 22.035C8.23565 21.067 7.51155 19.9241 7.03197 18.673C7.01589 18.6237 6.98495 18.5807 6.94342 18.5497C6.90188 18.5187 6.85177 18.5014 6.79997 18.5H5.99997C5.44026 18.4565 4.88335 18.6137 4.42907 18.9436C3.9748 19.2734 3.65286 19.7543 3.52097 20.3C3.51225 20.3563 3.48463 20.408 3.44265 20.4465C3.40066 20.485 3.34682 20.5081 3.28997 20.512C2.52701 20.5476 1.80817 20.88 1.2869 21.4382C0.765629 21.9965 0.483226 22.7364 0.499972 23.5Z"
                fill="#B5C2F0"
              />
              <path
                d="M10.25 15.478C9.99123 15.4698 9.73359 15.515 9.49306 15.6107C9.25254 15.7064 9.03427 15.8505 8.85184 16.0342C8.66941 16.2178 8.52672 16.4371 8.43263 16.6782C8.33855 16.9194 8.29509 17.1773 8.30496 17.436C8.30496 18.667 9.57296 20.236 10.062 20.792C10.0854 20.8188 10.1143 20.8402 10.1468 20.8549C10.1792 20.8696 10.2144 20.8772 10.25 20.8772C10.2856 20.8772 10.3207 20.8696 10.3532 20.8549C10.3856 20.8402 10.4145 20.8188 10.438 20.792C10.926 20.235 12.195 18.668 12.195 17.436C12.2048 17.1773 12.1614 16.9194 12.0673 16.6782C11.9732 16.4371 11.8305 16.2178 11.6481 16.0342C11.4656 15.8505 11.2474 15.7064 11.0069 15.6107C10.7663 15.515 10.5087 15.4698 10.25 15.478Z"
                fill="#B5C2F0"
              />
              <path
                d="M12.646 2.492C12.2446 2.21368 11.8189 1.97235 11.374 1.771C11.3243 1.74688 11.2841 1.70702 11.2595 1.65764C11.2349 1.60826 11.2273 1.55213 11.238 1.498C11.2472 1.45123 11.2519 1.40368 11.252 1.356V1C11.252 0.734784 11.1466 0.48043 10.9591 0.292893C10.7715 0.105357 10.5172 0 10.252 0C9.98674 0 9.73239 0.105357 9.54485 0.292893C9.35732 0.48043 9.25196 0.734784 9.25196 1V1.356C9.25201 1.40368 9.2567 1.45123 9.26596 1.498C9.27659 1.55213 9.26901 1.60826 9.24441 1.65764C9.21982 1.70702 9.17957 1.74688 9.12996 1.771C8.68521 1.9721 8.25977 2.21344 7.85896 2.492C7.43451 2.85753 7.104 3.31959 6.89518 3.83936C6.68637 4.35913 6.60536 4.92142 6.65896 5.479V5.489L7.78696 10.619C7.79955 10.6775 7.79085 10.7385 7.76243 10.7911C7.73402 10.8437 7.68775 10.8845 7.63196 10.906L7.47596 10.966C7.03906 11.1349 6.66534 11.4352 6.40634 11.8255C6.14735 12.2158 6.01584 12.6768 6.02996 13.145C6.10996 15.919 6.11696 15.72 8.57296 14.16H11.923L13.551 15.195C13.6354 15.2486 13.7325 15.2788 13.8325 15.2827C13.9324 15.2865 14.0316 15.2638 14.1199 15.2168C14.2082 15.1699 14.2825 15.1004 14.3352 15.0154C14.3879 14.9304 14.4171 14.833 14.42 14.733L14.466 13.146C14.4796 12.6772 14.3473 12.2158 14.0873 11.8255C13.8274 11.4352 13.4527 11.1352 13.015 10.967L12.859 10.907C12.8032 10.8855 12.7571 10.8447 12.7288 10.792C12.7006 10.7394 12.6921 10.6783 12.705 10.62C12.774 10.306 13.756 5.793 13.84 5.48C13.8944 4.92276 13.8145 4.36058 13.6067 3.84065C13.3989 3.32073 13.0695 2.85824 12.646 2.492ZM10.252 6.68C9.99737 6.68 9.74851 6.60449 9.53684 6.46303C9.32517 6.32157 9.16021 6.12051 9.06283 5.88528C8.96545 5.65006 8.94002 5.39123 8.98976 5.14155C9.0395 4.89187 9.16218 4.66255 9.34227 4.4826C9.52236 4.30265 9.75177 4.18015 10.0015 4.13061C10.2512 4.08106 10.51 4.10669 10.7452 4.20425C10.9803 4.30182 11.1813 4.46693 11.3225 4.67871C11.4638 4.89049 11.5392 5.13941 11.539 5.394C11.539 5.56296 11.5057 5.73027 11.441 5.88636C11.3763 6.04245 11.2815 6.18426 11.1619 6.30369C11.0424 6.42312 10.9005 6.51783 10.7444 6.5824C10.5883 6.64696 10.4209 6.68013 10.252 6.68Z"
                fill="#B5C2F0"
              />
            </svg>
            Get started
          </button>
          <img
            src={LogoFooter}
            className="block mx-auto"
            alt="AICargo - Bring your models to life"
          />
        </div>
      </main>
    </Fragment>
  );
}
