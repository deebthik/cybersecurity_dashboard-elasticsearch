# Use Node.js official image
FROM node:16-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json from the host machine into the container
COPY package.json package-lock.json .

# Install dependencies
RUN npm install

# Copy the rest of the frontend code into the container
COPY src src
COPY public public

# Expose port 3000 for React app
EXPOSE 3000

# Command to run the React app
CMD ["npm", "start"]
