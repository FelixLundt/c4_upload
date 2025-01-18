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

# Copy c4utils package to root level
echo "Copying c4utils package..."
mkdir -p deploy_tmp/c4utils
cp -r ../c4utils/c4utils/* deploy_tmp/c4utils/

# Debug: Show deployment directory structure
echo "Deployment directory structure:"
ls -R deploy_tmp/

# Create modified requirements.txt for deployment
echo "Creating deployment requirements.txt..."
cat > deploy_tmp/requirements.txt << EOL
# Web app dependencies
flask>=2.0.0
google-cloud-storage>=2.0.0
google-cloud-logging>=3.0.0
python-dotenv>=0.19.0
gunicorn>=20.1.0  # For production server

# c4utils dependencies
numpy>=1.24.0
docker>=7.0.0
EOL

# Create modified app.yaml for deployment
echo "Creating deployment app.yaml..."
cat > deploy_tmp/app.yaml << EOL
runtime: python310

# Region configuration
service: default
env: standard
instance_class: F1

# This tells App Engine how to run your app
entrypoint: gunicorn -b :8080 main:app

# Environment variables for production
env_variables:
  DOMAIN: "c4league.fans"
  TEAM1_PASSWORD: "secretpassword1"
  TEAM2_PASSWORD: "secretpassword2"
  TEAM3_PASSWORD: "secretpassword3"
  TEAM1_NAME: "team1"
  TEAM2_NAME: "team2"
  TEAM3_NAME: "team3"
EOL

# Deploy to GCP
echo "Deploying to Google Cloud Platform..."
cd deploy_tmp && gcloud app deploy --quiet --verbosity=debug

# Clean up
echo "Cleaning up..."
cd ..
rm -rf deploy_tmp

echo "Deployment complete!" 