# Serverless REST API on Google Cloud Functions

A minimal Serverless REST API with three endpoints (`/hello`, `/users`, `/stats`) built using:

- **Google Cloud Functions (1st-gen)**
- **API Gateway**
- **Deployment Manager** (IaC for automation)

---

## Project Structure

```

serverless-api/
│
├── functions/
│   ├── hello/          # Code for /hello endpoint
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── users/          # Code for /users endpoint
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   └── stats/          # Code for /stats endpoint
│       ├── main.py
│       └── requirements.txt
│
├── apigateway/
│   └── api-config.yaml # OpenAPI spec for API Gateway
│
├── deployment-manager/
│   └── deployment.yaml # Deployment Manager template for hello\_world
│
└── README.md

```

---

## Endpoints (Deployed)

1. **GET /hello**  
   Returns:
   ```text
   Hello from Yash’s first GCP function!
   ```

````

2. **GET /users**
   Returns:

   ```json
   { "users": ["alice", "bob", "carol"] }
   ```

3. **GET /stats**
   Returns:

   ```json
   { "active_users": 23, "uptime": "99.9%" }
   ```

Once you deploy via API Gateway, all three will live under one base URL:

```
https://<GATEWAY_ID>-uc.a.run.app
```

So you can call:

```
curl https://<GATEWAY_ID>-uc.a.run.app/hello
curl https://<GATEWAY_ID>-uc.a.run.app/users
curl https://<GATEWAY_ID>-uc.a.run.app/stats
```

---

## How to Deploy (MVP)

### 1. Prerequisites

* A GCP project with billing enabled (e.g. `YOUR_PROJECT_ID`)
* GCP APIs enabled:

  * Cloud Functions API
  * API Gateway API
  * Cloud Deployment Manager API
  * (Optional) Cloud Build API
* Installed and initialized Google Cloud SDK (`gcloud init`)

### 2. Deploy Cloud Functions (1st-gen)

From `serverless-api` root:

```bash
# 2.1 Deploy hello_world
gcloud functions deploy hello_world \
  --runtime python311 \
  --trigger-http \
  --entry-point hello_world \
  --allow-unauthenticated \
  --region us-central1 \
  --source=functions/hello \
  --no-gen2

# 2.2 Deploy get_users
gcloud functions deploy get_users \
  --runtime python311 \
  --trigger-http \
  --entry-point get_users \
  --allow-unauthenticated \
  --region us-central1 \
  --source=functions/users \
  --no-gen2

# 2.3 Deploy get_stats
gcloud functions deploy get_stats \
  --runtime python311 \
  --trigger-http \
  --entry-point get_stats \
  --allow-unauthenticated \
  --region us-central1 \
  --source=functions/stats \
  --no-gen2
```

*Wait for each deployment to complete. Note each function’s URL.*

### 3. Set Up API Gateway

1. Edit `apigateway/api-config.yaml`:

   * Replace `YOUR_PROJECT_ID` in each `address:` field with your real project ID.

2. Create the API, config, and gateway:

   ```bash
   # 3.1 Create the API resource
   gcloud api-gateway apis create serverless-api \
     --project=YOUR_PROJECT_ID

   # 3.2 Create the API config from the OpenAPI spec
   gcloud api-gateway api-configs create serverless-api-config \
     --api=serverless-api \
     --openapi-spec=apigateway/api-config.yaml \
     --project=YOUR_PROJECT_ID

   # 3.3 Create the Gateway to serve that API
   gcloud api-gateway gateways create serverless-gateway \
     --api=serverless-api \
     --api-config=serverless-api-config \
     --location=us-central1 \
     --project=YOUR_PROJECT_ID
   ```

3. Once the gateway is up (it may take \~1–2 minutes), note the “defaultHostname” it prints, e.g.:

   ```
   https://<GATEWAY_ID>-uc.a.run.app
   ```

4. Test each route:

   ```bash
   curl https://<GATEWAY_ID>-uc.a.run.app/hello
   curl https://<GATEWAY_ID>-uc.a.run.app/users
   curl https://<GATEWAY_ID>-uc.a.run.app/stats
   ```

### 4. (Optional) Automate `hello_world` with Deployment Manager

To automate just the `hello_world` function:

1. Ensure you have a GCS bucket (replace `YOUR_BUCKET_NAME`):

   ```bash
   gsutil mb -p YOUR_PROJECT_ID gs://YOUR_BUCKET_NAME
   ```

2. Zip and upload your function source:

   ```bash
   cd functions/hello
   zip -r hello_source.zip main.py requirements.txt
   gsutil cp hello_source.zip gs://YOUR_BUCKET_NAME/
   cd ../../
   ```

3. Edit `deployment-manager/deployment.yaml` and replace:

   * `YOUR_PROJECT_ID`
   * `YOUR_BUCKET_NAME`
     in `sourceArchiveUrl: gs://YOUR_BUCKET_NAME/hello_source.zip`

4. Create or update the deployment:

   ```bash
   gcloud deployment-manager deployments create hello-deployment \
     --config=deployment-manager/deployment.yaml \
     --project=YOUR_PROJECT_ID

   # If you modify the code & reupload the zip:
   gcloud deployment-manager deployments update hello-deployment \
     --config=deployment-manager/deployment.yaml \
     --project=YOUR_PROJECT_ID
   ```

---

````
