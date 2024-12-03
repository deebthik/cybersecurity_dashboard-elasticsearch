from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch, NotFoundError
from pydantic import BaseModel
from elasticsearch.helpers import bulk
import schedule
import time
import threading
from subprocess import run
from generate_2 import main as generate_2
from generate import main as generate


# FastAPI setup
app = FastAPI()

# Enable CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Elasticsearch setup
es = Elasticsearch(
    hosts=["https://localhost:9200"],
    basic_auth=("elastic", "9ksWiz-YIsUE*vxzk*eV"),  # Add your username and password here
    verify_certs=False
)

# Delete all documents from the index "incidents"
index_name = "incidents"
response = es.delete_by_query(index=index_name, body={
    "query": {
        "match_all": {}  # Match all documents
    }
})

# Pydantic models
class Incident(BaseModel):
    title: str
    description: str
    severity: str
    attack_type: str

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    attack_type: str

from elasticsearch import Elasticsearch

# Function to calculate number of shards and replicas based on criteria
def calculate_shards_and_replicas(data_volume: int, traffic_volume: int):
    # Basic logic for dynamic shard and replica settings
    # Increase number of shards as data volume grows
    if data_volume > 1000000:  # Example condition for large data
        num_shards = 5
    else:
        num_shards = 3  # Default value for moderate data

    # Increase number of replicas for higher traffic or fault tolerance needs
    if traffic_volume > 1000:  # Example condition for high traffic
        num_replicas = 3
    else:
        num_replicas = 2  # Default number of replicas

    return num_shards, num_replicas

# Elasticsearch setup
es = Elasticsearch(
    hosts=["https://localhost:9200"],
    basic_auth=("elastic", "9ksWiz-YIsUE*vxzk*eV"),
    verify_certs=False
)

@app.on_event("startup")
async def startup_event():
    index_name = "incidents"
    
    # Determine data volume (e.g., number of existing records)
    existing_data = es.count(index=index_name)
    data_volume = existing_data["count"]  # The current number of documents in the index

    # Assume some logic for traffic volume, for now, we use a placeholder value
    traffic_volume = 500  # This could be calculated dynamically based on API usage or similar

    # Calculate shards and replicas dynamically
    num_shards, num_replicas = calculate_shards_and_replicas(data_volume, traffic_volume)

    # Check if the index exists, if not, create it with dynamic settings
    if not es.indices.exists(index=index_name):
        index_settings = {
            "settings": {
                "number_of_shards": num_shards,
                "number_of_replicas": num_replicas
            },
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "severity": {"type": "keyword"},
                    "attack_type": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }
        es.indices.create(index=index_name, body=index_settings)

from datetime import datetime

# Define the bulk insert function that runs the curl command
def bulk_insert():

    curr_dt = datetime.now()
    timestamp = int(round(curr_dt.timestamp()))

    # switching between both for demonstration purposes
    if timestamp%2 == 0:
        print("external API generation")
        #the generate_2 function called generate_2.py which fetches CVE data from a online database, this is to show that this implementation can support external real-time APIs
        generate_2()
    else:
        print("random data generating locally")
        #there is a generate function randomly generates 50,000 data points to show how much load the implementation can handle
        generate()

    command = [
        "curl", 
        "-k", 
        "-u", "elastic:9ksWiz-YIsUE*vxzk*eV", 
        "-X", "POST", 
        "https://localhost:9200/incidents/_bulk", 
        "-H", "Content-Type: application/json", 
        "--data-binary", "@sample_incidents.json"
    ]
    run(command)

bulk_insert()
# Schedule the task to run every hour
#schedule.every(1).hour.do(bulk_insert)
schedule.every(1).minute.do(bulk_insert)


# Function to run scheduled tasks
def start_periodic_task():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Start the periodic task in a separate thread (to avoid blocking FastAPI's event loop)
periodic_task_thread = threading.Thread(target=start_periodic_task)
periodic_task_thread.start()

# Routes for incidents
@app.get("/search")
async def search_incidents(
    query: str = Query(None),
    severity: str = None,
    attack_type: str = None,
    page: int = 1,
    size: int = 10
):
    from_result = (page - 1) * size

    body = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        },
        "size": size,
        "from": from_result
    }

    if query:
        # Fuzzy matching query for the `title` field
        body["query"]["bool"]["must"].append({
            "match": {
                "title": {
                    "query": query,
                    "fuzziness": "AUTO"  # Automatically adjust the fuzziness level
                }
            }
        })

    if severity:
        body["query"]["bool"]["filter"].append({"term": {"severity.keyword": severity}})

    if attack_type:
        body["query"]["bool"]["filter"].append({"term": {"attack_type.keyword": attack_type}})

    results = es.search(index="incidents", body=body)

    total_results = results["hits"]["total"]["value"]

    return {
        "results": [hit["_source"] for hit in results["hits"]["hits"]],
        "total": total_results,
        "page": page,
        "size": size,
        "total_pages": (total_results // size) + (1 if total_results % size > 0 else 0)
    }


@app.get("/aggregations")
async def get_aggregations():
    aggregation_query = {
        "size": 0,
        "aggs": {
            "severity_count": {
                "terms": {
                    "field": "severity.keyword",
                    "size": 10
                }
            },
            "attack_type_count": {
                "terms": {
                    "field": "attack_type.keyword",
                    "size": 10
                }
            }
        }
    }

    response = es.search(index="incidents", body=aggregation_query)

    severity_aggregations = response['aggregations']['severity_count']['buckets']
    attack_type_aggregations = response['aggregations']['attack_type_count']['buckets']

    return {
        "severity_count": [
            {"severity": bucket["key"], "count": bucket["doc_count"]} for bucket in severity_aggregations
        ],
        "attack_type_count": [
            {"attack_type": bucket["key"], "count": bucket["doc_count"]} for bucket in attack_type_aggregations
        ]
    }

@app.post("/incidents", response_model=IncidentResponse)
async def add_incident(incident: Incident):
    response = es.index(index="incidents", body=incident.dict())
    incident_id = response["_id"]
    return {**incident.dict(), "id": incident_id}

@app.put("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: str, incident: Incident):
    try:
        es.get(index="incidents", id=incident_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")

    es.update(index="incidents", id=incident_id, body={"doc": incident.dict()})
    return {**incident.dict(), "id": incident_id}

@app.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: str):
    try:
        es.get(index="incidents", id=incident_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")

    es.delete(index="incidents", id=incident_id)
    return {"message": "Incident deleted successfully"}
