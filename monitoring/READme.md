

# 📊 Monitoring the Iris API with Prometheus & Grafana

This guide details how to set up a robust monitoring stack for the FastAPI application using **Prometheus** for metrics collection and **Grafana** for visualization, all running on a Kubernetes cluster.

## Overview of the Monitoring Architecture

Monitoring is crucial for understanding the performance and health of our machine learning API in a production-like environment. Our setup uses a "declarative" or "Kubernetes-native" approach to monitoring.

Here's how the components interact:

1. **FastAPI Application**: The Python code is instrumented with `prometheus-fastapi-instrumentator`, which exposes an HTTP endpoint at `/metrics` with key performance indicators (KPIs) like request latency, counts, and error rates.
    
2. `ServiceMonitor`: This is a custom Kubernetes resource (`CRD`) provided by the Prometheus Operator. Instead of manually configuring Prometheus, we create a `ServiceMonitor` object. This object tells the Prometheus Operator to find our application's service and automatically add its `/metrics` endpoint to the list of scrape targets.
    
3. **Prometheus**: An open-source monitoring system that periodically "scrapes" (pulls) metrics from the `/metrics` endpoint. It stores this time-series data efficiently, allowing us to query it.
    
4. **Grafana**: An open-source visualization tool. We configure Grafana to use Prometheus as a data source. We then build or import dashboards in Grafana to create graphs, alerts, and tables from the metrics stored in Prometheus.
    
5. **Ingress**: A Kubernetes resource that manages external access to services within the cluster. We use it to expose the Prometheus and Grafana web UIs on user-friendly hostnames ([`prometheus.example.com`](http://prometheus.example.com), [`grafana.example.com`](http://grafana.example.com)).
    

---

## Prerequisites

Before you begin, ensure you have the following:

* A running Kubernetes cluster (e.g., AKS, GKE, EKS, or local like Minikube).
    
* `kubectl` command-line tool configured to communicate with your cluster.
    
* `helm` (v3) command-line tool for package management in Kubernetes.
    
* The Iris FastAPI application deployed in your cluster with a `Service` and `Deployment` in the `default` namespace. The service must have the label `app: iris-api`.
    
* An Nginx Ingress Controller deployed in your cluster. If you don't have one, you can install it with Helm:
    
    Bash
    
    ```bash
    helm upgrade --install ingress-nginx ingress-nginx \
      --repo https://kubernetes.github.io/ingress-nginx \
      --namespace ingress-nginx --create-namespace
    ```
    

---

##  Step-by-Step Monitoring Setup

### Step 1: Deploy the Prometheus & Grafana Stack

We'll use the `kube-prometheus-stack` Helm chart, which bundles Prometheus, Grafana, Alertmanager, and the crucial **Prometheus Operator** that enables the use of `ServiceMonitor`.

**a. Add the required Helm repository:**

This command adds the Prometheus community chart repository to your Helm client, making the `kube-prometheus-stack` chart available for installation.

Bash

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

**b. Install the chart:**

This command installs the stack into a dedicated `monitoring` namespace. The `release: monitoring` label is added to all resources, which we'll use later to associate our `ServiceMonitor`.

Bash

```bash
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

*Note: The* `serviceMonitorSelectorNilUsesHelmValues=false` flag allows Prometheus to discover `ServiceMonitor` resources in other namespaces, not just those with a matching release label.

### Step 2: Create the `ServiceMonitor`

Now, we create the `ServiceMonitor` to tell Prometheus how to find and scrape our `iris-api`.

**a. Create a file named** `service-monitor.yaml`:

YAML

```bash
# service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  # The name of our monitor
  name: iris-api-monitor
  # Must be deployed in the same namespace as Prometheus
  namespace: monitoring
  # This label connects the monitor to the Prometheus Operator instance installed by Helm
  labels:
    release: monitoring
spec:
  # This selector tells the ServiceMonitor which Kubernetes Services to target.
  # It will look for any Service with the label "app: iris-api".
  selector:
    matchLabels:
      app: iris-api
  # This selector specifies which namespaces to look for the Service in.
  # We are telling it to look in the "default" namespace where our app is deployed.
  namespaceSelector:
    matchNames:
      - default
  # This defines the specifics of the metrics endpoint on the targeted Service.
  endpoints:
    - port: http # The name of the port in your Service definition.
      path: /metrics # The path where metrics are exposed.
      interval: 15s # How frequently Prometheus should scrape the metrics.
```

**b. Apply the manifest to your cluster:**

Bash

```
kubectl apply -f service-monitor.yaml
```

Prometheus will now automatically detect and begin scraping metrics from your `iris-api` application.

### Step 3: Expose Prometheus and Grafana via Ingress

To access the web UIs for Prometheus and Grafana, we create Ingress rules.

**a. Create a files named** `prometheus-ingress.yaml`, `grafana-ingress.yaml`:

This file defines rules to route traffic from specific hostnames to the internal Prometheus and Grafana services.

YAML

```
# monitoring-ingress.yaml

# Ingress for Grafana
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: monitoring
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: grafana.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                # The service for Grafana created by the Helm chart
                name: monitoring-grafana
                port:
                  number: 80
```
---
```
# Ingress for Prometheus
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prometheus-ingress
  namespace: monitoring
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: prometheus.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                # The service for Prometheus created by the Helm chart
                name: monitoring-kube-prometheus-prometheus
                port:
                  number: 9090
```

**b. Apply the manifest to your cluster:**

Bash

```bash
kubectl apply -f  prometheus-ingress.yaml
kubectl apply -f  grafana-ingress.yaml
```

### Step 4: Configure Local DNS (for local testing)

To make [`grafana.example.com`](http://grafana.example.com) and [`prometheus.example.com`](http://prometheus.example.com) work from your local machine, you need to map them to your Ingress controller's external IP address.

**a. Find your Ingress Controller's IP:**

Bash

```bash
kubectl get svc -n ingress-nginx
# Look for the EXTERNAL-IP of the ingress-nginx-controller service
```

**b. Edit your local** `hosts` file:

Add the following lines to your `/etc/hosts` file (on Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (on Windows), replacing `<YOUR-INGRESS-EXTERNAL-IP>` with the IP from the previous step.

```bash
<YOUR-INGRESS-EXTERNAL-IP> grafana.example.com
<YOUR-INGRESS-EXTERNAL-IP> prometheus.example.com
```

### Step 5: Access Grafana and Visualize 📈

**a.  Get the Grafana admin password:**

The Helm chart auto-generates a password and stores it in a Kubernetes secret.

Bash

```bash
kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

**b. Log in to Grafana:**

Open your browser and navigate to [`http://grafana.example.com`](http://grafana.example.com). Log in with the username `admin` and the password you just retrieved.

**c. Import the FastAPI Dashboard:**

We will use a pre-built community dashboard for FastAPI.

1. In the Grafana UI, go to the **Dashboards** section.
    
2. Click on **New** and then **Import**.
    
3. In the "Import via [grafana.com](http://grafana.com)" box, enter the dashboard ID: `18739`.
    
4. Click **Load**.
    
5. On the next screen, you'll be asked to select a Prometheus data source. Choose the one named `Prometheus`.
    
6. Click **Import**.
    

You should now see a dashboard visualizing the live metrics from your Iris API! It will show HTTP request rates, error rates, latencies by path, and more.

---
![Prometheus](/assets/images/prometheus.png)
---
![grafana](/assets/images/grafana.png)
---
![grafana-fastapi-dashboard](/assets/images/grafana-dashboard.png)
---


## Importing the Grafana Dashboard

This project includes a pre-built Grafana dashboard definition file (`grafana-dashboard.json`) to save you time. Follow these steps to import and use it.

### Step 1: Access the Grafana UI

Log in to your Grafana instance, which should be accessible at `http://grafana.example.com` (if you set up Ingress) or via `port-forwarding`.

### Step 2: Navigate to the Import Menu

1. In the left-hand menu, go to **Dashboards**.
    
2. On the Dashboards page, click the **\+ New** button and select **Import**.
    

### Step 3: Upload the Dashboard JSON

You will see the "Import dashboard" screen.

1. Click the **Upload JSON file** button.
    
2. Navigate to the project directory on your local machine and select the `grafana/grafana-dashboard.json` file.
    

### Step 4: Configure and Import

1. After uploading, Grafana will show you the dashboard options.
    
2. **Crucially**, you must select your Prometheus data source from the dropdown menu at the bottom of the page.
    
3. Click the **Import** button.
    

The "FastAPI Observability" dashboard will now load with all its panels, and you can start monitoring your application's metrics immediately.