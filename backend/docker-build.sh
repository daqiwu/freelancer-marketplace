#!/bin/bash
# Docker Build and Run Script for Poetry-based Backend
# This script demonstrates how to build and run the containerized application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Freelancer Marketplace - Backend Docker${NC}"
echo -e "${BLUE}  Build Tool: Poetry${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Build the Docker image
echo -e "${YELLOW}📦 Building Docker image with Poetry...${NC}"
docker build -t freelancer-backend:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}\n"
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# Optional: Run the container
read -p "Do you want to run the container now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚀 Starting container...${NC}"
    
    # Load environment variables from .env file if it exists
    ENV_FILE=""
    if [ -f ".env" ]; then
        ENV_FILE="--env-file .env"
        echo -e "${GREEN}📝 Using .env file for configuration${NC}"
    else
        echo -e "${YELLOW}⚠️  No .env file found. Using default configuration.${NC}"
    fi
    
    # Run the container
    docker run -d \
        --name freelancer-backend \
        -p 8000:8000 \
        $ENV_FILE \
        freelancer-backend:latest
    
    echo -e "${GREEN}✅ Container started!${NC}"
    echo -e "${BLUE}📊 API Documentation: http://localhost:8000/docs${NC}"
    echo -e "${BLUE}📝 Container logs: docker logs -f freelancer-backend${NC}"
    echo -e "${BLUE}🛑 Stop container: docker stop freelancer-backend${NC}"
    echo -e "${BLUE}🗑️  Remove container: docker rm freelancer-backend${NC}"
fi

echo -e "\n${GREEN}Done! 🎉${NC}"
