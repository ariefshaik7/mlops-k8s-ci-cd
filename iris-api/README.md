

# Iris Species Classification API 

This project provides a machine learning-powered REST API to classify Iris flower species based on their sepal and petal measurements. The API is built using **FastAPI**, and the application is containerized with **Docker** for easy deployment and scalability.

##  Features

* **RESTful API**: Provides a simple and intuitive interface for predictions.
    
* **High Performance**: Built with FastAPI and Uvicorn for asynchronous, high-speed performance.
    
* **Data Validation**: Uses Pydantic for robust request data validation.
    
* **Containerized**: A Dockerfile is included for easy environment setup and deployment.
    
* **Monitoring Ready**: Exposes Prometheus-compatible metrics at the `/metrics` endpoint.
    
* **Classic ML Problem**: Utilizes the well-known Iris dataset and a Scikit-learn `RandomForestClassifier`.
    

---

##  Technology Stack

* **Language**: Python 3.11
    
* **ML Framework**: Scikit-learn
    
* **API Framework**: FastAPI
    
* **Server**: Uvicorn
    
* **Containerization**: Docker
    
* **Data Validation**: Pydantic
    
* **Monitoring**: Prometheus FastAPI Instrumentator
    

---

##  Project Structure

Here is the recommended project directory structure:

```bash
mlops-app/
├── app/
│   ├── main.py             # FastAPI application logic
│   └── requirements.txt    # Python dependencies
├── model/
│   └── model.pkl           # Trained machine learning model
├── dataset/
│   └── Iris.csv            # Dataset for training
├── notebooks/
│   └── train_model.ipynb   # Script to train the model
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

---

##  Getting Started

### Prerequisites

* [Docker](https://www.docker.com/get-started) installed on your machine.
    
* [Python 3.11+](https://www.python.org/downloads/) for running the training script.
    
* An API client like [curl](https://curl.se/) or [Postman](https://www.postman.com/) to test the endpoints.
    

### 1\. Train the Model

First, you need to train the model, which will be saved to the `model/` directory.

Bash

```bash
# Navigate to the training script directory
cd mlops-app/notebooks

# Install dependencies
pip install -r ../app/requirements.txt

pip install notebook

# Run the training script
jupyter notebook train_model.ipynb
```

This will create the `model/model.pkl` file.

### 2\. Build and Run the Docker Container

With the model file in place, you can build the Docker image and run the container.

Bash

```bash
# Navigate to the project root directory
cd mlops-app

# Build the Docker image
docker build -t iris-classifier-api .

# Run the Docker container
docker run -d -p 8000:8000 --name iris-api iris-classifier-api
```

The API will now be accessible at `http://localhost:8000`.

---

## ↔️ API Endpoints

The API provides the following endpoints:

### Health Check

* **Endpoint**: `/`
    
* **Method**: `GET`
    
* **Description**: Confirms that the API is live and running.
    
* **Success Response**:
    
    JSON
    
    ```bash
    {
      "Messsage": "Iris Species API is Live!"
    }
    ```
    

### Predict Species

* **Endpoint**: `/predict`
    
* **Method**: `POST`
    
* **Description**: Predicts the Iris species based on input features.
    
* **Request Body**:
    
    JSON
    
    ```bash
    {
      "Id": 1,
      "SepalLengthCm": 5.1,
      "SepalWidthCm": 3.5,
      "PetalLengthCm": 1.4,
      "PetalWidthCm": 0.2
    }
    ```
    
* **Success Response**:
    
    JSON
    
    ```bash
    {
      "predicted_species": "Iris-setosa"
    }
    ```
    
* **Example** `curl` Request:
    
    Bash
    
    ```bash
    curl -X 'POST' \
      'http://localhost:8000/predict' \
      -H 'Content-Type: application/json' \
      -d '{
            "Id": 1,
            "SepalLengthCm": 5.1,
            "SepalWidthCm": 3.5,
            "PetalLengthCm": 1.4,
            "PetalWidthCm": 0.2
          }'
    ```
  
---
![fastapi](/assets/images/fastapi.png)
---
![fastapi](/assets/images/fastapi-input.png)
---
![fastapi](/assets/images/fastapi-output.png)
---
