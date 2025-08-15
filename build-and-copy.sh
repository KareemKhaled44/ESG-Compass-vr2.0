#!/bin/bash

# Build React app
cd frontend-react
npm install
npm run build

# Copy dist folder to backend
cd ..
cp -r frontend-react/dist backend/

echo "Build complete! React app copied to backend/dist/"