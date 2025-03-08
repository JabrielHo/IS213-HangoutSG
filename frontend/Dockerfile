# Stage 1: Build Stage
FROM node:20 AS build

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY package.json package-lock.json ./
RUN npm install

# Copy source code
COPY . .

# Build Vue app
RUN npm run build

# Stage 2: Serve Stage
FROM nginx:alpine

# Copy built files from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for NGINX
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
