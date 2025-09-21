# Google Cloud Platform Deployment Guide

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed and configured
3. **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# Make the script executable
chmod +x deploy-gcp.sh

# Deploy to Google Cloud
./deploy-gcp.sh YOUR_PROJECT_ID us-central1
```

### Option 2: Manual Deployment

1. **Set up Google Cloud Project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

3. **Create API Key Secret**
   ```bash
   echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
   ```

4. **Deploy with Cloud Build**
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

## Configuration Options

### Environment Variables

The application supports the following environment variables:

- `GEMINI_API_KEY`: Your Gemini API key (stored as secret)
- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port number (automatically set by Cloud Run)

### Cloud Run Settings

- **Memory**: 1GB (configurable in cloudbuild.yaml)
- **CPU**: 1 vCPU (configurable in cloudbuild.yaml)
- **Timeout**: 300 seconds (5 minutes)
- **Max Instances**: 10 (auto-scaling)
- **Region**: us-central1 (configurable)

## Cost Optimization

### Estimated Costs

- **Cloud Run**: ~$0.40 per 1M requests
- **Cloud Build**: ~$0.003 per build minute
- **Container Registry**: ~$0.10 per GB per month
- **Secret Manager**: ~$0.06 per 10,000 operations

### Cost-Saving Tips

1. **Use Cloud Run's pay-per-use model** - only pay when serving requests
2. **Set appropriate max instances** to control scaling costs
3. **Use Gemini 2.0 Flash-Lite** for better API quota efficiency
4. **Monitor usage** through Google Cloud Console

## Security Best Practices

### Implemented Security Features

- **Non-root container user** for enhanced security
- **Secret Manager** for API key storage
- **No data persistence** - documents processed in memory only
- **HTTPS enforcement** by default on Cloud Run
- **IAM controls** for deployment and access

### Additional Security Recommendations

1. **Enable Cloud Armor** for DDoS protection
2. **Set up Cloud Monitoring** for anomaly detection
3. **Use VPC connectors** if connecting to private resources
4. **Regular security updates** of base images

## Monitoring and Logging

### Built-in Monitoring

- **Health checks** at `/health` endpoint
- **Cloud Logging** integration
- **Error reporting** through Google Cloud
- **Performance metrics** in Cloud Run console

### Viewing Logs

```bash
# View recent logs
gcloud run logs tail genai-legal-assistant --region=us-central1

# View logs in real-time
gcloud run logs tail genai-legal-assistant --region=us-central1 --follow
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Docker syntax in Dockerfile
   - Verify all dependencies in requirements.txt
   - Ensure sufficient build timeout

2. **Deployment Failures**
   - Verify project permissions
   - Check API enablement
   - Confirm secret creation

3. **Runtime Errors**
   - Check application logs
   - Verify environment variables
   - Test API key validity

### Debug Commands

```bash
# Check service status
gcloud run services describe genai-legal-assistant --region=us-central1

# View build history
gcloud builds list --limit=10

# Test local Docker build
docker build -t genai-legal-assistant .
docker run -p 8080:8080 genai-legal-assistant
```

## Updating the Application

### Automatic Updates

Any push to the main branch will trigger a new build and deployment if you set up Cloud Build triggers.

### Manual Updates

```bash
# Redeploy with latest changes
./deploy-gcp.sh YOUR_PROJECT_ID us-central1
```

## Cleanup

### Remove Resources

```bash
# Delete Cloud Run service
gcloud run services delete genai-legal-assistant --region=us-central1

# Delete container images
gcloud container images delete gcr.io/YOUR_PROJECT_ID/genai-legal-assistant --force-delete-tags

# Delete secrets
gcloud secrets delete gemini-api-key
```

## Support

For deployment issues:
1. Check Google Cloud Console for detailed error messages
2. Review Cloud Build logs for build failures
3. Monitor Cloud Run logs for runtime issues
4. Verify API quotas and billing status

## Architecture Overview

```
User Request → Cloud Load Balancer → Cloud Run → Container → Flask App
                                                      ↓
                                              Gemini API (via Secret Manager)
                                                      ↓
                                              Response → PDF Generation → User
```

This deployment provides a scalable, secure, and cost-effective solution for the GenAI Legal Assistant on Google Cloud Platform.