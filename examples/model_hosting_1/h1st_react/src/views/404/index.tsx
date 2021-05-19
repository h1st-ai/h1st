// import FourSvg from "./img/404.svg";

import { APP_PREFIX } from "config";

export default function Four0four() {
  return (
    <div className="max-w-3xl mx-auto my-40 text-center">
      <h1 className="text-3xl text-blue-900 mb-4">
        What you're looking for is not here
      </h1>
      <p>
        The content you're looking for may have been moved or its privacy
        setting has changed .
      </p>
      <a
        href={`/${APP_PREFIX}/dashboard`}
        className="items-center inline-flex mx-auto my-6 font-bold tracking-wide hover:text-blue-700"
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
        Back to the dashboard
      </a>
      {/* <img src={FourSvg} alt="Page not found" /> */}
    </div>
  );
}
