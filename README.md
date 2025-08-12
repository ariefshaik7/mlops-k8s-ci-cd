

# MLOps CI/CD Pipeline for Iris Classification API

[](https://www.google.com/search?q=https://github.com/ariefshaik7/mlops-k8s-ci-cd/actions/workflows/deploy.yml)

This repository contains a complete, end-to-end MLOps project demonstrating how to build, test, deploy, and monitor a machine learning model as a scalable API. The pipeline leverages **GitHub Actions** for CI/CD and **Argo CD** for GitOps-based continuous deployment to a **Kubernetes** cluster.

##  Technology Stack

| Category              | Technology                                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------------------------- |
| **ML & API** | Python, Scikit-learn, FastAPI, Pydantic, Uvicorn                                                            |
| **Containerization** | Docker                                                                                                      |
| **Orchestration** | Kubernetes (GKE, AKS, EKS, Minikube, kind)                                                                  |
| **CI/CD** | GitHub Actions                                                                                              |
| **Continuous Deploy** | Argo CD (GitOps)                                                                                            |
| **IaC & Packaging** | Helm                                                                                                        |
| **Monitoring** | Prometheus, Grafana                                                                                         |

-----

##  Project Structure

The repository is organized to separate concerns, making it modular and easy to navigate.

```
mlops-k8s-ci-cd/
├── .github/workflows/      # CI/CD pipelines defined for GitHub Actions
│   └── deploy.yml          # Workflow to build, push Docker image, and update Helm chart
├── argocd/                 # Argo CD application manifest
│   └── argocd-app.yaml     # Declarative definition of our application for Argo CD
├── helm/iris-api-chart/    # Helm chart for deploying the Iris API
│   ├── templates/          # Kubernetes manifest templates (Deployment, Service, Ingress)
│   ├── Chart.yaml          # Information about the chart
│   └── values.yaml         # Default configuration values for the chart (image tag, replicas, etc.)
├── iris-api/               # Source code for the FastAPI application
│   ├── app/                # Main application logic
│   ├── dataset/            # Iris dataset used for training
│   ├── model/              # Saved Scikit-learn model file
│   ├── notebooks/          # Jupyter notebook for model training
│   └── Dockerfile          # Instructions to build the application's Docker image
├── monitoring/             # Manifests and guide for setting up the monitoring stack
|   ├── grafana
|   |   └── grafana-dashboard.json  # Pre-built Grafana dashboard definition file
│   ├── grafana-ingress.yaml
│   ├── prometheus-ingress.yaml
│   ├── README.md           # Detailed guide for setting up monitoring
│   └── service-monitor.yaml
└── README.md               # This main project guide
```

-----

##  End-to-End Deployment Guide

Follow these steps to deploy the entire stack from scratch.

### Step 0: Prerequisites

Ensure you have the following command-line tools installed:

  * `git`
  * `docker`
  * `kubectl`
  * `helm`
  * A Cloud CLI if using a managed Kubernetes service (e.g., `gcloud`, `az`, `aws`/`eksctl`)

### Step 1: Set Up a Kubernetes Cluster

Create a Kubernetes cluster on your preferred platform. Here are the minimal commands. For a more detailed guide, see the **[Kubernetes Cluster Setup Guide](https://www.google.com/search?q=./docs/cluster-setup.md)**.

  * **GKE (Google Cloud):**
    ```bash
    gcloud container clusters create "my-gke-cluster" --zone "us-central1-c"
    gcloud container clusters get-credentials "my-gke-cluster" --zone "us-central1-c"
    ```
  * **AKS (Azure):**
    ```bash
    az group create --name "MyResourceGroup" --location "eastus"
    az aks create --resource-group "MyResourceGroup" --name "myAKSCluster" --generate-ssh-keys
    az aks get-credentials --resource-group "MyResourceGroup" --name "myAKSCluster"
    ```
  * **EKS (AWS, with `eksctl`):**
    ```bash
    eksctl create cluster --name my-eks-cluster --region us-west-2 --nodes 2
    ```
  * **Minikube (Local):**
    ```bash
    minikube start
    ```
  * **kind (Local):**
    ```bash
    kind create cluster
    ```

### Step 2: Configure GitHub Secrets

The CI/CD pipeline requires secrets to push to Docker Hub and commit to your repository.

1.  **Fork this repository** to your own GitHub account.
2.  In your forked repository, go to `Settings > Secrets and variables > Actions`.
3.  Create the following secrets:
      * `DOCKERHUB_USERNAME`: Your Docker Hub username.
      * `DOCKERHUB_PASSWORD`: Your Docker Hub password or access token.
      * `GIT_PAT`: A GitHub Personal Access Token with `repo` scope. This is required for the workflow to push the updated `values.yaml` back to your repository.

### Step 3: The CI/CD Pipeline (Automated)

The CI/CD process is defined in `.github/workflows/deploy.yml` and is triggered automatically on a `git push` to the `master` branch.

**What it does:**

1.  **Job 1 (`docker`):**
      * Logs into Docker Hub using your secrets.
      * Builds a new Docker image from the `iris-api/Dockerfile`.
      * Tags the image with a unique ID from the GitHub run (`<your-dockerhub-username>/iris-api:${{ github.run_id }}`).
      * Pushes the new image to Docker Hub.
2.  **Job 2 (`update-newtag-in-helm`):**
      * Waits for the `docker` job to succeed.
      * Checks out the repository code.
      * Uses `sed` to replace the old image `tag` in `helm/iris-api-chart/values.yaml` with the new tag from the previous job.
      * Commits and pushes the updated `values.yaml` file back to your repository.

**To trigger the pipeline, simply make a code change and push it to the `master` branch.**

### Step 4: Continuous Deployment with Argo CD

Argo CD will monitor your repository and automatically deploy any changes. This is the core of the **GitOps** workflow.

**a. Install Argo CD on your cluster:**

```bash
# Create a dedicated namespace for Argo CD
kubectl create namespace argocd

# Apply the official Argo CD installation manifest
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**b. Get the initial Argo CD admin password:**

The password is created as a Kubernetes secret.

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

**c. Expose the Argo CD Server (Optional, for UI access):**

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

You can now access the Argo CD UI at `https://localhost:8080`. Log in with username `admin` and the password from the previous step.

**d. Deploy the Iris API Application:**

The `argocd/argocd-app.yaml` file tells Argo CD where your application's configuration lives (i.e., your Git repository's Helm chart path).

**Important:** Before applying, edit `argocd/argocd-app.yaml` and change the `repoURL` to point to **your forked repository's URL**.

```yaml
# argocd/argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: iris-api
  namespace: argocd
spec:
  project: default
  source:
    # CHANGE THIS TO YOUR FORKED REPO URL
    repoURL: 'https://github.com/YOUR-USERNAME/mlops-k8s-ci-cd.git'
    path: 'helm/iris-api-chart'
    targetRevision: HEAD
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply this manifest to your cluster. Argo CD will immediately detect it, clone your repository, render the Helm chart, and deploy the Iris API to the `default` namespace.

```bash
kubectl apply -f argocd/argocd-app.yaml
```

From now on, every time the GitHub Actions pipeline updates the image tag in `values.yaml`, Argo CD will automatically detect the change in Git and update the running application in Kubernetes to use the new image.

---
![argocd](/assets/images/argocd.png)


-----

## 📊 Monitoring the Application

The application is instrumented to expose performance metrics. You can set up a complete Prometheus and Grafana stack to visualize these metrics.

The repository includes a pre-configured Grafana dashboard definition at grafana/grafana-dashboard.json that can be imported directly.
For a complete, step-by-step guide, please see the **[Monitoring README](/monitoring/READme.md)**.

-----

Of course. Here is the updated `Cleanup` section with specific commands for each cloud provider.

## 🧹 Cleanup

To avoid ongoing cloud provider costs, delete the resources when you are finished.

---

### Cloud Clusters

* **GKE (Google Kubernetes Engine):**
    
    Bash
    
    ```bash
    gcloud container clusters delete "my-gke-cluster" --zone "us-central1-c"
    ```
    
* **AKS (Azure Kubernetes Service):**
    
    Bash
    
    ```bash
    az group delete --name "MyResourceGroup" --yes --no-wait
    ```
    
* **EKS (Amazon Elastic Kubernetes Service):**
    
    Bash
    
    ```bash
    eksctl delete cluster --name my-eks-cluster --region us-west-2
    ```
    

---

### Local Clusters

* **Minikube:**
    
    Bash
    
    ```bash
    minikube delete
    ```
    
* **kind:**
    
    Bash
    
    ```bash
    kind delete cluster
    ```