#!/bin/bash

# Build and run script for Water Analysis Application

IMAGE_NAME="water-analysis"
CONTAINER_NAME="water-app"
PORT="3000"

echo "Building Water Analysis Docker image..."

# Build the Docker image
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Stop and remove existing container if it exists
    docker stop $CONTAINER_NAME 2>/dev/null
    docker rm $CONTAINER_NAME 2>/dev/null
    
    echo "Starting container on port $PORT..."
    
    # Run the container
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:$PORT \
        --restart unless-stopped \
        $IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "🌐 Application available at: http://localhost:$PORT"
        echo ""
        echo "Useful commands:"
        echo "  View logs: docker logs -f $CONTAINER_NAME"
        echo "  Stop app:  docker stop $CONTAINER_NAME"
        echo "  Remove:    docker rm $CONTAINER_NAME"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
else
    echo "❌ Build failed"
    exit 1
fi
