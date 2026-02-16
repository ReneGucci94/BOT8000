# Cloud Run Deployment Script
# Usage: ./deploy-cloud-run.sh

PROJECT_ID="gen-lang-client-0740921908"
SERVICE_NAME="bot8000"
REGION="us-central1"

echo "🚀 Building and deploying BOT8000 to Cloud Run..."

# Build
echo "📦 Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=${DATABASE_URL}" \
  --set-env-vars="TRADING_MODE=simulation" \
  --memory=1Gi \
  --cpu=1 \
  --concurrency=80 \
  --max-instances=3 \
  --min-instances=1

echo "✅ Deployment complete!"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
