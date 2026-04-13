# Use official Node.js Alpine image
FROM node:24.11.1-alpine
# Set the working directory
WORKDIR /usr/src/app

# Copy package.json to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Expose the port Node runs on
EXPOSE 5000