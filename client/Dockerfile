FROM node:22-alpine

WORKDIR /app

# Build arg for base path: "/verify" for subpath hosting, "" for dedicated domain
ARG NEXT_PUBLIC_BASE_PATH="/verify"
ENV NEXT_PUBLIC_BASE_PATH=${NEXT_PUBLIC_BASE_PATH}

COPY package.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
