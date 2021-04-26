[![yarn version](https://badge.fury.io/js/cra-template-typescript-redux.svg)](https://badge.fury.io/js/cra-template-typescript-redux)
[![Action status](https://github.com/alexandr-g/cra-template-typescript-redux/workflows/CI/badge.svg?branch=master)](https://github.com/alexandr-g/cra-template-typescript-redux/actions)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
![yarn downloads](https://img.shields.io/npm/dm/cra-template-typescript-redux)

# A quick start Redux + TypeScript Create React App template

An opinionated quick start [Create React App](https://github.com/facebook/create-react-app) (CRA) _template_ with configured **Redux**, **TypeScript**, **React Router**, **Enzyme** and custom **ESlint** configuration.

Original Create React App README available [here](./README_CRA.md)

## Usage

```bash
npx create-react-app your-project-name --template typescript-redux
```

Or

```bash
yarn create react-app your-project-name --template typescript-redux
```

`npx` command installs the most recent stable version of CRA from npm.

`--template` parameter points to this template, note that `cra-template-` prefix is omitted.

## Motivation

You know the pain. You start a new project from scratch and need to configure it again and again. It needs routing, ok you setup Router, then you need Redux - ok, oh 😩 Redux boilerplate is taking so much time to type. Wait... what if you could have all the tools you want just from the beginning? I want to focus on building amazing projects and not spending hours configuring. That's why I've created this template. It's here for you to use.

## Available Scripts

In the project directory, you can run:

- `yarn start` - runs the app in the development mode. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

- `yarn test` - launches the test runner in the interactive watch mode.

- `yarn build` - builds the app for production to the `build` folder.

- `yarn eject` - exposes content of `react-script` package

- `yarn lint` - lints project files according to eslint rules, see below. Typical use case: continuous integration environments, Travis, CircleCI, etc.

- `yarn fix` - same as `yarn lint`, but also fixes errors, when possible. Typical use case: local development environment, git hooks.

Due to CRA template limitations (we can change only `scripts` and `dependencies` inside generated `package.json`) all configuration is done by adding config files where possible. Also no `devDependencies` for now, sorry.

## Redux configuration

The template provides basic Redux configuration with [feature based](https://redux.js.org/style-guide/style-guide/#structure-files-as-feature-folders-or-ducks) folder structure. You can use [Redux devtools browser extension](http://extension.remotedev.io/). Sample feature included in `src/features` folder, note technology agnostic `features` folder name. Based on Redux maintainers recommendation.

## Testing

Testing is done with [Enzyme](https://airbnb.io/enzyme/).

## [Prettier](https://prettier.io/)

I added `prettier` to force consistent formatting. Don't like trailing semicolons? Feel free to [tweak prettier rules](https://prettier.io/docs/en/configuration.html) inside `.prettierrc` file to match your code style.

## Styles/CSS/Styling

Just for the styling purpose of the example app, I used [Materialize](https://materializecss.com/). The template is shipped with the Materialize by default. I want to make sure that this template is style agnostic so you can plugin any CSS-in-JS or whatever library/framework you want to use for styles on your own.

### How to remove materialize

In order to remove Materialize [MaterializeCSS](https://materializecss.com/) navigate to the `public` folder, open `index.html` and remove following CDN link in the `<head>` lines 18-22:

```html
<!--Import materialize.css-->
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"
/>
```

Remove or adjust all the `classNames` related to the Materialize and feel free to use your own styling.

## Eslint configurations

The template extends CRA ESLint rules with a custom set, tailored for the reasonable and clean development process.

Eslint rules are commented for your convenience feel free to tweak or remove them inside `.eslintrc`. No judgment.

## Testing template locally

To test the output of your template locally run

```bash
npx create-react-app my-app --template file:/\path\to\file
```

## How to create custom Create React App (CRA) templates

I created a step by step guide on how to create your own templates.

[View on Medium](https://medium.com/@alexgrischuk/how-to-create-custom-create-react-app-cra-templates-73a5196edeb)

[View on personal blog](https://grischuk.de/how-to-create-custom-create-react-app-cra-templates)

[View on dev.to](https://dev.to/alexandrg/how-to-create-custom-create-react-app-cra-templates-3nca)

## My other templates

[A light weight Create React App template with Recoil for state management](https://github.com/alexandr-g/cra-template-recoil)

## Thank you

I hope this template will be helpful for you and you will love using it 🖤
