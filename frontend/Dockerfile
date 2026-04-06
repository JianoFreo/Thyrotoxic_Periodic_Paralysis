FROM node:18-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application source
COPY . .

EXPOSE 8080

# Start Vite dev server bound to all interfaces on the documented port
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8080"]
