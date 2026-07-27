FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Build the app (optional for dev server, but good practice if we want to run production)
# For the hackathon, running the dev server is fine to support hot-reloading
# RUN npm run build

# Expose Vite port
EXPOSE 5173

# Run the dev server and bind to 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
