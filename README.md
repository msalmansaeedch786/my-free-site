# Connection Identity Web Server

A modern, beautifully designed web application that parses a visitor's HTTP connection details and displays their exact IP address, browser, operating system, and device. 

This project is built to run **100% free** on the Google Cloud Run "Always Free" tier.

## Project Structure

This directory contains everything needed to run and deploy the application:

- `main.py`: The core Python Flask application logic.
- `templates/index.html`: The HTML/CSS frontend featuring a premium Glassmorphism design and animated mesh gradient.
- `requirements.txt`: Python dependencies (`Flask`, `user-agents`, `gunicorn`).
- `Dockerfile`: Instructions for containerizing the application using a lightweight Python image.
- `main.tf`: The Infrastructure as Code (Terraform) configuration that defines the Google Cloud resources.

## Zero-Cost Infrastructure Architecture

This project is meticulously configured to stay within the Google Cloud "Always Free" tier limits, resulting in a **$0.00 monthly bill**.

1. **Google Cloud Run (Compute)**: Runs the application container. The Terraform configuration strictly enforces a limit of **1 maximum instance** (`max_instance_count = 1`) and minimal memory (`256Mi`). This guarantees it will never exceed the free allocation of 2 million requests and 180,000 vCPU-seconds per month, even under heavy traffic.
2. **Google Cloud Storage (Remote State)**: The Terraform state is securely stored in a GCS bucket (`tf-state-gen-lang-client-0111574187`). This uses less than 1MB of the 5GB free monthly allowance.
3. **Artifact Registry**: Stores the compiled Docker image (~150MB), sitting comfortably under the 500MB free tier limit.

## Running Locally

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask development server:
   ```bash
   python main.py
   ```
4. Open your browser and navigate to `http://localhost:8080`.

## Cloud Deployment Guide

This project uses a hybrid deployment model. If you have just cloned this repository, follow the **First-Time Setup** instructions.

### 1. First-Time Setup (Deploying from scratch)

If you are deploying this to a new Google Cloud project, you must set up the state bucket and push the initial code before running Terraform.

**Step A: Authenticate and Set Project**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

**Step B: Create the Terraform State Bucket**
Terraform needs a remote bucket to securely store the state. Create it using the CLI (replace `YOUR_PROJECT_ID` with your actual project ID):
```bash
gcloud storage buckets create gs://tf-state-YOUR_PROJECT_ID --location=us-central1
```
*Note: Update `bucket = "..."` in the `main.tf` file to match this new bucket name, and update the `project = "..."` field as well.*

**Step C: Initial Code Deployment**
Before Terraform can manage the Cloud Run service, you need to deploy the initial code so that the Docker image exists in the Artifact Registry:
```bash
gcloud run deploy my-free-site --source . --region us-central1 --allow-unauthenticated
```

**Step D: Initialize and Apply Terraform**
Now that the code is deployed, lock down the infrastructure settings (like the 1-instance limit) using Terraform:
```bash
terraform init
terraform apply
```

---

### 2. Routine Updates (CI/CD)

The old manual CLI deployments have been replaced by a fully automated **GitHub Actions CI/CD pipeline**.

**How to update your code:**
1. Make your changes locally.
2. Commit and push to the `main` branch:
   ```bash
   git add .
   git commit -m "Your feature description"
   git push origin main
   ```
3. GitHub Actions will automatically take over! It will:
   - Run `pytest` to check for bugs and `black` to check code formatting.
   - Build a new Docker container tagged with your exact git commit hash.
   - Upload it to the Google Artifact Registry.
   - Run `terraform apply` to instantly push the new image to Google Cloud Run safely.

**How to update infrastructure:**
If you need to change memory limits, environment variables, or scaling settings, simply edit `main.tf` and push it to the `main` branch. The CI/CD pipeline will automatically detect the changes and apply them during the deploy step.
