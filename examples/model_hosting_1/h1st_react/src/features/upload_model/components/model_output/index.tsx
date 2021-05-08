import { useState } from "react";
import { RadioGroup } from "@headlessui/react";

const settings = [
  {
    name: "Image Classifier",
    value: "IMG_CLASSIFER",
    enabled: true,
    description: "Expose your application as an image classifier.",
  },
  {
    name: "NLP",
    value: "NLP_CLASSIFER",
    enabled: false,
    description: "coming soon.",
  },

  // {
  //   name: "REST API",
  //   value: "REST",
  //   description: "Expose your application as a REST API.",
  // },
  // {
  //   name: "Web Application",
  //   description: "Create an web applicaiton with user interface",
  // },
];

// @ts-ignore
function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function ModelOutput() {
  const [selected, setSelected] = useState(settings[0].value);

  return (
    <RadioGroup value={selected} onChange={setSelected}>
      <RadioGroup.Label className="sr-only">Privacy setting</RadioGroup.Label>
      <div className="bg-white rounded-md -space-y-px">
        {settings.map((setting, settingIdx) => (
          <RadioGroup.Option
            // @ts-ignore
            disabled={!setting.enabled}
            key={setting.name}
            value={setting.value}
            className={({ checked }) =>
              classNames(
                setting.enabled ? "" : "pointer-events-none",
                settingIdx === 0 ? "rounded-tl-md rounded-tr-md" : "",
                settingIdx === settings.length - 1
                  ? "rounded-bl-md rounded-br-md"
                  : "",
                checked
                  ? "bg-indigo-50 border-indigo-200 z-10"
                  : "border-gray-200",
                "relative border p-4 flex cursor-pointer focus:outline-none",
                "disabled:opacity-50"
              )
            }
          >
            {({ active, checked }) => (
              <>
                <span
                  className={classNames(
                    checked
                      ? "bg-indigo-600 border-transparent"
                      : "bg-white border-gray-300",
                    active ? "ring-2 ring-offset-2 ring-indigo-500" : "",
                    "h-4 w-4 mt-0.5 cursor-pointer rounded-full border flex items-center justify-center"
                  )}
                  aria-hidden="true"
                >
                  <span className="rounded-full bg-white w-1.5 h-1.5" />
                </span>
                <div className="ml-3 flex flex-col">
                  <RadioGroup.Label
                    as="span"
                    className={classNames(
                      checked ? "text-indigo-900" : "text-gray-900",
                      "block text-sm font-medium"
                    )}
                  >
                    {setting.name}
                  </RadioGroup.Label>
                  <RadioGroup.Description
                    as="span"
                    className={classNames(
                      checked ? "text-indigo-700" : "text-gray-500",
                      "block text-sm"
                    )}
                  >
                    {setting.description}
                  </RadioGroup.Description>
                </div>
              </>
            )}
          </RadioGroup.Option>
        ))}
      </div>
    </RadioGroup>
  );
}
