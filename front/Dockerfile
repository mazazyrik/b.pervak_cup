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
RUN npm ci && npm run build

FROM nginx:1.27-alpine AS runtime
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./
EXPOSE 80
CMD nginx -g 'daemon off;'

