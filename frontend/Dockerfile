# Stage 1 - Build
FROM node:14 as react-build
WORKDIR /app
COPY package.json ./package.json
COPY yarn.lock ./yarn.lock
RUN yarn install
COPY . ./
RUN REACT_APP_ENV=${REACT_APP_ENV} yarn build

# Stage 2 - Serve
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/nginx.conf
COPY --from=react-build /app/build /var/www/tamane-mziane
RUN rm /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
