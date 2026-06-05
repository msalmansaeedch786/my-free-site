# Connection Identity Web Server

A modern, beautifully designed web application that parses a visitor's HTTP connection details and displays their exact IP address, browser, operating system, and device. 

This project is built to run **100% free** on the Google Cloud Run "Always Free" tier, powered by an enterprise-grade GitHub Actions CI/CD pipeline and strict Infrastructure as Code.

## Project Structure

This directory contains everything needed to run, test, and deploy the application:

### Application Code
- `main.py`: The core Python Flask application logic.
- `templates/index.html`: The frontend featuring a premium Glassmorphism design and animated mesh gradient.
- `requirements.txt`: Production dependencies (`Flask`, `user-agents`, `gunicorn`).

### Testing & Quality (Application Hardening)
- `tests/test_main.py`: Automated `pytest` unit tests to verify the routing and parsing logic.
- `requirements-dev.txt`: Development dependencies (`pytest`, `black`).
- `.gitignore`: Ensures environments and secrets are never accidentally pushed to GitHub.

### Infrastructure & Deployment
- `main.tf`: Strict Terraform configuration defining Google Cloud resources, including the Artifact Registry.
- `Dockerfile`: Instructions for containerizing the application.
- `.github/workflows/deploy.yml`: The CI/CD pipeline that automatically tests, lints, builds, and deploys the app on every push to the `main` branch.

## Zero-Cost Infrastructure Architecture

This project is meticulously configured to stay within the Google Cloud "Always Free" tier limits, resulting in a **$0.00 monthly bill**.

1. **Google Cloud Run**: Runs the application container. The Terraform configuration enforces a limit of **1 maximum instance** (`max_instance_count = 1`) and minimal memory (`256Mi`). 
2. **Google Artifact Registry**: The `main.tf` file creates a dedicated Docker repository (`my-free-site-repo`). Since the container uses a lightweight Alpine/Slim image (~150MB), it easily fits in the 500MB free allowance.
3. **Google Cloud Storage**: The remote Terraform state is securely stored in a GCS bucket, taking up less than 1MB of the 5GB free allowance.

## Local Development

### Option A: Using Docker (Recommended)
You can run the exact same container locally that runs in Google Cloud:
1. Build the image:
   ```bash
   docker build -t my-free-site .
   ```
2. Run the container:
   ```bash
   docker run -e PORT=8080 -p 8080:8080 my-free-site
   ```
3. Visit `http://localhost:8080` in your browser.

### Option B: Native Python
1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. **Run the Server:**
   ```bash
   python main.py
   ```
4. **Run the Tests:**
   ```bash
   pytest tests/
   ```
5. **Format your Code:**
   ```bash
   black .
   ```

## Deployment Workflow (CI/CD)

This project uses a fully automated **GitHub Actions CI/CD pipeline**.

### 1. First-Time Setup (Deploying from scratch)
If you just cloned this repository and are deploying to a brand new Google Cloud project, you must set up the foundation *before* the CI/CD pipeline can run.

**Prerequisites:** Ensure you have installed the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install), [Terraform](https://developer.hashicorp.com/terraform/downloads), and [Docker](https://docs.docker.com/get-docker/) before proceeding.

**Step A: Authenticate locally**
```bash
gcloud auth login
gcloud auth application-default login
```

**Step B: Create the Remote State Bucket**
Terraform needs a secure place to store its state. Create a bucket (and update `main.tf` to match its name):
```bash
gcloud storage buckets create gs://tf-state-YOUR_PROJECT_ID --location=us-central1
```

**Step C: Create the Artifact Registry**
The CI/CD pipeline needs a place to push your Docker image. Run Terraform *only* for the registry first to solve the "chicken and egg" problem:
```bash
terraform init
terraform apply -target=google_artifact_registry_repository.my_repo
```

**Step D: Add Secrets to GitHub**
The CI/CD pipeline needs permission to deploy to your Google Cloud project. Run these exact commands to generate a secure key:
```bash
# 1. Create a Service Account
gcloud iam service-accounts create github-actions-sa --display-name="GitHub Actions"

# 2. Grant it the Editor role (Replace YOUR_PROJECT_ID below)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

# 3. Download the JSON key file
gcloud iam service-accounts keys create sa-key.json \
    --iam-account=github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```
Finally, copy the entire contents of `sa-key.json` and add it as a **Repository Secret** in GitHub named exactly `GCP_CREDENTIALS`. *(Delete the `sa-key.json` file from your computer immediately after!)*

Once this foundation is set, proceed to the daily workflow below!

### 2. Daily Development (Automated CI/CD)
When you want to update the app, you do not need to use the `gcloud` or `terraform` CLI tools anymore.
1. Make your code changes locally.
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your description"
   git push origin main
   ```
3. GitHub Actions takes over! It will automatically:
   - Run `black` to check code formatting.
   - Run `pytest` to ensure your code works.
   - Build a new Docker container tagged with your exact git commit hash.
   - Upload the container to the Google Artifact Registry.
   - Run `terraform apply` to push the new image to Cloud Run.

### 2. Infrastructure Changes
If you ever want to increase the memory limit or add an environment variable, simply edit `main.tf` and push it to GitHub. The CI/CD pipeline will automatically detect the changes and apply them to Google Cloud safely.
