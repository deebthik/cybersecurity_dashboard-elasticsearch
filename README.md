# Cybersecurity Dashboard

This project is a dashboard for managing and searching security incident data using Elasticsearch, FastAPI, and React.js. It provides a powerful search interface and allows you to efficiently manage and analyze incidents.

## Features

- **Elastic Search Optimization**:
  - Sharding and replication for handling large datasets.
  - Aggregation support for summarizing data, such as incident counts by severity or attack type.

- **Large Dataset Integration**:
  - Integration of large datasets of incidents from public sources.
  - Automatic downloading and indexing of new security incident data into Elasticsearch at regular intervals.

- **Advanced Search Functionality**:
  - Fuzzy matching and real-time suggestions for searching incident titles and descriptions.
  - Advanced filters for severity, attack type, affected system, and timestamp range.
  - Flexible querying with wildcard or prefix search.

- **Incident Management**:
  - Add, update, and delete incidents directly through the backend.
  - Bulk data upload functionality for incidents in formats like JSON or CSV.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Docker and Docker Compose
- Node.js and npm
- Python 3.8+ and pip
- Basic knowledge of command-line tools

## Setting Up the Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cybersecurity-dashboard

2. **Launch Elasticsearch using Docker**
```bash
  docker pull docker.elastic.co/elasticsearch/elasticsearch:8.9.1
  docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.9.1

  Verify elasticsearch is running
  ```bash
  curl -X GET "localhost:9200"

3. **Set up the backend**
    ```bash
      pip install -r requirements.txt
        uvicorn main:app --reload --port 8001

4. **Set up the frontend**
  ```bash
    npm install
    npm start


**Features in Detail**

1. Elasticsearch Optimization
Implement sharding and replication for improved performance and high availability.
Use Elasticsearch’s aggregation capabilities for summarized data insights, such as counting incidents by severity or attack type.

2. Large Dataset Integration
Integrate large datasets by importing security incidents from public data sources like Kaggle, security reports, or public feeds.
Set up automated scripts to download and index new data periodically.

3. Advanced Search Functionality
Use fuzzy matching for better search results in incident titles and descriptions.
Enhance search functionality with advanced filters, such as severity, attack type, and timestamp range.

4. Incident Management
The backend supports creating, updating, and deleting incidents.
Bulk upload incidents using the Elasticsearch bulk API with data in JSON or CSV formats.
