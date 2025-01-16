#!/bin/bash

# Set the GCP project
PROJECT_ID="c4league"  # Replace with your actual project ID
echo "Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Create a temporary deployment directory
echo "Creating deployment directory..."
rm -rf deploy_tmp
mkdir deploy_tmp

# Copy webapp files
echo "Copying webapp files..."
cp -r app deploy_tmp/
cp -r main.py deploy_tmp/

# Copy c4utils package
echo "Copying c4utils package..."
mkdir -p deploy_tmp/c4utils
cp -r ../c4utils/c4utils/* deploy_tmp/c4utils/

# Create modified requirements.txt for deployment
echo "Creating deployment requirements.txt..."
cat > deploy_tmp/requirements.txt << EOL
flask>=2.0.0
google-cloud-storage>=2.0.0
python-dotenv>=0.19.0
gunicorn>=20.1.0  # For production server
/home/vmagent/app/c4utils  # Local package at absolute deployment path
EOL

# Create modified app.yaml for deployment
echo "Creating deployment app.yaml..."
cat > deploy_tmp/app.yaml << EOL
runtime: python39

# This tells App Engine how to run your app
entrypoint: gunicorn -b :$PORT main:app

# Environment variables for production
env_variables:
  C4UTILS_PATH: "/home/vmagent/app/c4utils"  # Absolute path in App Engine environment
  # Add a reminder to set these in the GCP Console
  # TEAM1_PASSWORD: "your-password-here"
  # TEAM2_PASSWORD: "your-password-here"

# Service account configuration
service_account: default  # Use the default App Engine service account

# Files that should be included
includes:
- app/**
- c4utils/**
- requirements.txt
- main.py
EOL

echo "REMINDER: Make sure to set your team passwords in the GCP Console under:"
echo "App Engine -> Settings -> Environment Variables"
echo ""
echo "REMINDER: Make sure the App Engine default service account has the necessary permissions:"
echo "- Storage Object Viewer"
echo "- Storage Object Creator"
echo ""

# Deploy to GCP
echo "Deploying to Google Cloud Platform..."
cd deploy_tmp && gcloud app deploy

# Clean up
echo "Cleaning up..."
cd ..
rm -rf deploy_tmp

echo "Deployment complete!" 