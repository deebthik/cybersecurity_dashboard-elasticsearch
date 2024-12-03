from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch, NotFoundError
from pydantic import BaseModel
from elasticsearch.helpers import bulk
import schedule
import time
import threading
from subprocess import run

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
    basic_auth=("elastic", "7uNhNxsb=vLD__GWi4M9"),  # Add your username and password here
    verify_certs=False
)

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

# Startup event to create index
@app.on_event("startup")
async def startup_event():
    index_name = "incidents"
    
    if not es.indices.exists(index=index_name):
        index_settings = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 2
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

# Define the bulk insert function that runs the curl command
def bulk_insert():
    command = [
        "curl", 
        "-k", 
        "-u", "elastic:7uNhNxsb=vLD__GWi4M9", 
        "-X", "POST", 
        "https://localhost:9200/incidents/_bulk", 
        "-H", "Content-Type: application/json", 
        "--data-binary", "@sample_incidents.json"
    ]
    run(command)

# Schedule the task to run every hour
schedule.every(1).hour.do(bulk_insert)

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
        body["query"]["bool"]["must"].append({"match": {"title": query}})

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
