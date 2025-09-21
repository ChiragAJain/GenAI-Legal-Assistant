#!/bin/bash

# GenAI Legal Assistant - Google Cloud Run Deployment Script

echo " Deploying GenAI Legal Assistant to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo " Google Cloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "  GEMINI_API_KEY environment variable is not set."
    echo "   Please set it with: export GEMINI_API_KEY='your-api-key-here'"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    exit 1
fi

# Set project variables
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="genai-legal-assistant"
REGION="us-central1"

echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to Cloud Run
echo "Building and deploying..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10

if [ $? -eq 0 ]; then
    echo "Deployment successful!"
    echo "Your GenAI Legal Assistant is now live!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    echo "URL: $SERVICE_URL"
    
    echo ""
    echo "Next steps:"
    echo "   1. Test your deployment by visiting the URL above"
    echo "   2. Upload a legal document to test the GenAI features"
    echo "   3. Try the interactive Q&A functionality"
    echo ""
    echo "To update your deployment:"
    echo "   ./deploy.sh"
    echo ""
    echo "To view logs:"
    echo "   gcloud run logs tail $SERVICE_NAME --region=$REGION"
else
    echo "Deployment failed. Please check the error messages above."
    exit 1
fi