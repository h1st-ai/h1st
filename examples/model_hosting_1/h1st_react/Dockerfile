# build environment
FROM node:12 as build
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
COPY yarn.lock ./
# RUN yarn ci --silent
RUN yarn add react-scripts@3.4.1 -g --silent
RUN yarn global add serve
COPY . ./
RUN yarn run build

# production environment
CMD ["yarn", "serve", "build"]