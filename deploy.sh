#!/bin/bash

# Google Ads MCP Server - Cloud Run Deployment Script


# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"bbi-solutions-main"}
SERVICE_NAME="google-ads-mcp"
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
REPOSITORY="mcp-proxy"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}"

echo "🚀 Deploying Google Ads MCP Server to Cloud Run"
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"

# Build and push the container image
echo "📦 Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "PYTHONUNBUFFERED=1" \
  --set-env-vars "GOOGLE_ADS_CREDENTIALS=/app/google-ads.yaml"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')

echo "✅ Deployment completed!"
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "🔧 Next steps:"
echo "1. Configure OAuth2 credentials in Google Cloud Console"
echo "2. Set up the google-ads.yaml file with your credentials"
echo "3. Test the MCP server with an LLM client"
echo ""
echo "📖 MCP Server endpoint: ${SERVICE_URL}"
