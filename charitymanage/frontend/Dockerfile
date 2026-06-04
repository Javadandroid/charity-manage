FROM node:22-alpine

# Set work directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy project
COPY . .

# Expose port
EXPOSE 5173
