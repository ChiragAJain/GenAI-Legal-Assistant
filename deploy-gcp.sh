#!/bin/bash

# GenAI Legal Assistant - Google Cloud Platform Deployment Script

set -e  # Exit on any error

echo "🚀 Deploying GenAI Legal Assistant to Google Cloud Platform..."

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="genai-legal-assistant"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI is not installed.${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if project ID is provided
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}❌ Please provide your Google Cloud Project ID${NC}"
    echo "Usage: ./deploy-gcp.sh YOUR_PROJECT_ID [REGION]"
    echo "Example: ./deploy-gcp.sh my-legal-assistant-project us-central1"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service Name: $SERVICE_NAME"
echo ""

# Set the project
echo -e "${YELLOW}🔧 Setting up Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Check if GEMINI_API_KEY secret exists, if not create it
echo -e "${YELLOW}🔐 Setting up API key secret...${NC}"
if ! gcloud secrets describe gemini-api-key &> /dev/null; then
    echo -e "${YELLOW}Creating secret for Gemini API key...${NC}"
    echo "Please enter your Gemini API key:"
    read -s GEMINI_API_KEY
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
    echo -e "${GREEN}✅ Secret created successfully${NC}"
else
    echo -e "${GREEN}✅ Secret already exists${NC}"
fi

# Build and deploy using Cloud Build
echo -e "${YELLOW}🏗️ Building and deploying with Cloud Build...${NC}"
gcloud builds submit --config cloudbuild.yaml .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    echo ""
    echo -e "${GREEN}🎉 Your GenAI Legal Assistant is now live!${NC}"
    echo -e "${BLUE}🔗 URL: $SERVICE_URL${NC}"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "   1. Test your deployment by visiting the URL above"
    echo "   2. Upload a legal document to test the GenAI features"
    echo "   3. Try the interactive Q&A functionality"
    echo ""
    echo -e "${YELLOW}🔧 To update your deployment:${NC}"
    echo "   ./deploy-gcp.sh $PROJECT_ID $REGION"
    echo ""
    echo -e "${YELLOW}📊 To view logs:${NC}"
    echo "   gcloud run logs tail $SERVICE_NAME --region=$REGION"
    echo ""
    echo -e "${YELLOW}💰 To monitor costs:${NC}"
    echo "   Visit: https://console.cloud.google.com/billing"
    
else
    echo -e "${RED}❌ Deployment failed. Please check the error messages above.${NC}"
    exit 1
fi