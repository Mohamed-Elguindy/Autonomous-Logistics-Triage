# Use official Node.js image
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package.json so we can install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Expose the Vite port
EXPOSE 5173

# We don't COPY . here because we use volumes in docker-compose for dev