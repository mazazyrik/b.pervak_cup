FROM node:20-slim AS build
WORKDIR /app
COPY front/package*.json ./
COPY front/tsconfig*.json ./
COPY front/vite.config.ts ./
COPY front/tailwind.config.ts ./
COPY front/postcss.config.js ./
COPY front/index.html ./
COPY front/src ./src
COPY front/public ./public
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm ci && npx vite build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD nginx -g 'daemon off;'

