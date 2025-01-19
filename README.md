
# 🚖 Chicago Taxi Analytics Project

This project analyzes Chicago taxi trips and weather data to provide actionable insights into how weather conditions affect taxi operations. The data pipeline includes ingestion, transformation, and integration using Google Cloud Platform (GCP) services like BigQuery, Cloud Functions, and Cloud Scheduler.

---

## 📝 Project Overview

- **Data Sources**:
  - Chicago taxi trips data (`taxi-trips` table).
  - Weather data for Chicago (`weather_data` table).
- **Objective**:
  - Combine taxi trip data and weather data into a unified Data Mart for analysis.
  - Optimize queries by partitioning and filtering data.

---

### 🚀 Deployment Guide: Using `gcp-scheduled-function` Folder

The `terraform/gcp-scheduled-function` folder contains Terraform scripts and function code to deploy resources for automating data ingestion and processing in GCP. Follow these steps to deploy the necessary infrastructure and bulk-ingestion functionality.


##### 1. **Folder Contents**
- `main.tf`: Contains Terraform configurations for provisioning GCP resources, including:
  - **Pub/Sub Topic**: Used as a trigger for the Cloud Function.
  - **Cloud Scheduler**: Configured to publish messages to the Pub/Sub topic on a schedule.
  - **Cloud Function**: Executes on Pub/Sub messages to ingest weather data into BigQuery.


##### 2. **Environment Variables**

Both the Cloud Function and the local bulk ingestion function require an `.env` file to configure sensitive values. Create an `.env` file with the following variables:

```plaintext
WEATHER_API_KEY=<your_weather_api_key>
GCP_PROJECT_ID=<your_gcp_project_id>
BIGQUERY_DATASET_ID=<your_bigquery_dataset_id>
BIGQUERY_TABLE_NAME=<your_bigquery_table_name>
WEATHER_API_URL=http://api.weatherbit.io/v2.0/history/daily
```

**Note:** Replace `<your_weather_api_key>`, `<your_gcp_project_id>`, `<your_bigquery_dataset_id>`, and `<your_bigquery_table_name>` with your actual values. Do not commit the `.env` file to version control.



##### 3. **Deployment Instructions**

##### **Step 1: Set Up Your GCP Project**
1. Authenticate with Google Cloud CLI:
   ```bash
   gcloud auth login
   ```
2. Set your project ID:
   ```bash
   gcloud config set project [PROJECT_ID]
   ```

##### **Step 2: Deploy Resources with Terraform**
1. Navigate to the `gcp-scheduled-function` folder:
   ```bash
   cd gcp-scheduled-function
   ```
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Review the plan to ensure resources are provisioned correctly:
   ```bash
   terraform plan
   ```
4. Apply the Terraform configuration:
   ```bash
   terraform apply
   ```
   - This will provision the following:
     - **Pub/Sub Topic** for message publishing.
     - **Cloud Scheduler** to publish daily messages to the Pub/Sub Topic.
     - **Cloud Function** to fetch weather data and ingest it into BigQuery.

##### **Step 3: Verify the Deployment**
- Check the **Cloud Scheduler** job in the GCP Console to ensure it is scheduled to run as expected.
- Confirm that the **Cloud Function** is triggered by messages from the Pub/Sub topic.



#### 4. Running the Bulk Ingestion Locally

To fetch and ingest weather data into the `weather_data` table in BigQuery for a specific date range, follow these steps:


##### 1. **Set Up a Virtual Environment**
1. Navigate to the `local_bulk_ingest_function` folder:
   ```bash
   cd gcp-scheduled-function/local_bulk_ingest_function
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   - **Linux/MacOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```

4. Install dependencies into the virtual environment:
   ```bash
   pip install -r requirements.txt
   ```


##### 2. **Prepare the Environment**
1. Ensure your `.env` file is correctly configured in the `local_bulk_ingest_function` folder. Refer to the required variables listed in the deployment guide.

##### 3. **Run the Bulk Ingestion Function**
1. Execute the ingestion script:
   ```bash
   python ingest-bulk-weather-data/fetch_insert_bulk_data.py
   ```
   - This script will:
     - Fetch weather data for the specified date range from the Weather API.
     - Insert the data into the `weather_data` table in BigQuery.



## 📊 Architecture

### Key Components
1. **BigQuery**:
   - Stores raw and transformed data.
   - Includes staging and Data Mart tables for optimized analysis.
2. **Cloud Functions**:
   - Automates data ingestion (e.g., fetching weather data).
3. **Cloud Scheduler**:
   - Schedules the execution of the Cloud Function and queries.
4. **CI/CD Pipelines**:
   - Automates testing and deployment of the Cloud Function.
5. **Terraform**:
   - Manages the infrastructure-as-code for reproducibility.

---

## 🗂️ BigQuery Tables

### 1. **Raw Tables**:
- **Taxi Trips**:
  - Contains complete Chicago taxi trip data.
- **Weather Data**:
  - Stores daily weather information.

### 2. **Staging Tables**:
- Filtered and partitioned subsets of raw data:
  - **`staging_taxi_trips`**:
    - Filters trips between `2023-06-01` and `2023-12-31`.
    - Partitioned by `DATE(trip_start_timestamp)`.
  - **`staging_weather_data`**:
    - Filters weather data for the same date range.
    - Partitioned by `DATE(date)`.

### 3. **Data Mart**:
- Joins taxi trips and weather data for analysis:
  - **`data_mart_taxi_weather`**:
    - Combines staging tables.
    - Includes metrics like `trip_total` and `temperature`.

---

## 🚀 CI/CD Pipelines

The project includes two GitHub Actions pipelines:

1. **Testing Pipeline**:
   - Ensures code quality by running unit tests and linting before merging any code.
   - Triggered by Pull Requests.

2. **Deployment Pipeline**:
   - Automates the deployment of Cloud Functions to GCP.
   - Triggered by commits to the `main` branch.

---

## 🔧 Cloud Functions

### 1. **Weather Data Ingestion Function**
This Cloud Function fetches weather data from an external API and writes it to the `weather_data` table in BigQuery.

**Features**:
- Fetches daily weather data via a scheduled trigger.

---

## 🕒 Daily Workflow

1. **Cloud Scheduler** triggers:
   - Executes the Cloud Function to fetch and ingest new weather data.
2. **Scheduled Query** runs:
   - Updates staging tables and Data Mart.

---

## 🔍 Queries

### Create or Replace Tables

#### 1. Staging Taxi Trips
```sql
CREATE OR REPLACE TABLE `chicago-analytics-448011.chicago_analysis.staging_taxi_trips`
PARTITION BY DATE(trip_start_timestamp)
AS
SELECT *
FROM `chicago-analytics-448011.chicago_analysis.taxi-trips`
WHERE trip_start_timestamp BETWEEN '2023-06-01' AND '2023-12-31';
```

#### 2. Staging Weather Data
```sql
CREATE OR REPLACE TABLE `chicago-analytics-448011.chicago_analysis.staging_weather_data`
PARTITION BY DATE(date)
AS
SELECT *
FROM `chicago-analytics-448011.chicago_analysis.weather_data`
WHERE date BETWEEN '2023-06-01' AND '2023-12-31';
```

#### 3. Data Mart Table
```sql
CREATE OR REPLACE TABLE `chicago-analytics-448011.chicago_analysis.data_mart_taxi_weather`
AS
SELECT 
    t.unique_key as trip_id,
    t.trip_start_timestamp,
    t.trip_seconds,
    t.tips,
    t.trip_total,
    w.date,
    w.temperature,
    w.precipitation,
    w.wind_speed,
    w.snow_depth
FROM 
    `chicago-analytics-448011.chicago_analysis.staging_taxi_trips` t
JOIN 
    `chicago-analytics-448011.chicago_analysis.staging_weather_data` w
ON 
    DATE(t.trip_start_timestamp) = DATE(w.date);
```

---

### Looker Studio Dashboard

You can access the dashboard via the following link:

**[Access the Looker Studio Dashboard](https://lookerstudio.google.com/u/0/reporting/4eb14e44-87f4-40a0-aaf8-e27923dbf836/page/zD8dE)**

The dashboard is simple, containing two graphs:
1. A comparison of **trip duration** with **precipitation**.
2. A comparison of **trip duration** with **wind speed** for trips.
