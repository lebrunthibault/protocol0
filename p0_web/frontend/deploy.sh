#!/bin/bash

# Variables
DOCKER_IMAGE="thibaultlebrun/p0_web_frontend"
DOCKER_TAG="v5" # Change to a specific version if needed
K8S_DEPLOYMENT_NAME="frontend-deployment"
K8S_NAMESPACE="default" # Change if your deployment is in a different namespace

# Function to check for errors
check_error() {
    if [ $? -ne 0 ]; then
        echo "Error occurred in the last command. Exiting."
        exit 1
    fi
}

# Step 1: Build the Docker image
echo "Building Docker image..."
docker build -t "${DOCKER_IMAGE}:${DOCKER_TAG}" .
check_error

# Step 2: Log in to Docker Hub (optional if already logged in)
# Uncomment the next two lines if you want to log in via the script
# echo "Logging into Docker Hub..."
# echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
# check_error

# Step 3: Push the Docker image to Docker Hub
echo "Pushing Docker image to Docker Hub..."
docker push "${DOCKER_IMAGE}:${DOCKER_TAG}"
check_error

# Step 4: Update the Kubernetes deployment
echo "Updating Kubernetes deployment..."
minikube kubectl -- set image deployment/${K8S_DEPLOYMENT_NAME} frontend=${DOCKER_IMAGE}:${DOCKER_TAG} -n ${K8S_NAMESPACE}
check_error

# Step 5: Wait for rollout to complete
echo "Waiting for deployment to complete..."
minikube kubectl -- rollout status deployment/${K8S_DEPLOYMENT_NAME} -n ${K8S_NAMESPACE}
check_error

echo "Deployment completed successfully!"
