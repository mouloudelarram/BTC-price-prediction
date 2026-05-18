"""
Postman Collection for Mood Analysis API testing.

Import this into Postman to test all API endpoints.
"""

import json


def generate_postman_collection():
    """Generate Postman collection."""
    return {
        "info": {
            "name": "Crypto Market Mood Analysis API",
            "description": "Collection for testing the Mood Analysis API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Health & Info",
                "item": [
                    {
                        "name": "Health Check",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/health",
                                "host": ["{{base_url}}"],
                                "path": ["health"],
                            },
                        },
                    },
                    {
                        "name": "API Info",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/info",
                                "host": ["{{base_url}}"],
                                "path": ["info"],
                            },
                        },
                    },
                ],
            },
            {
                "name": "Scrapper",
                "item": [
                    {
                        "name": "Get Available Platforms",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/scrapper/platforms",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "scrapper", "platforms"],
                            },
                        },
                    },
                    {
                        "name": "Start Scraping",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "scrapper_type": "all",
                                    "platforms": ["twitter", "reddit"],
                                    "limit": 100,
                                }),
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/scrapper/run",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "scrapper", "run"],
                            },
                        },
                    },
                    {
                        "name": "Get Scraper Status",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/scrapper/job/{{job_id}}",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "scrapper", "job", "{{job_id}}"],
                            },
                        },
                    },
                    {
                        "name": "Get Latest Scraped Data",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/scrapper/latest",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "scrapper", "latest"],
                            },
                        },
                    },
                ],
            },
            {
                "name": "Mood Analysis",
                "item": [
                    {
                        "name": "Get Available Models",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/mood/models",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "mood", "models"],
                            },
                        },
                    },
                    {
                        "name": "Start Analysis",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "data_source": "scrapper",
                                    "batch_size": 5,
                                    "resume": False,
                                }),
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/mood/analyze",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "mood", "analyze"],
                            },
                        },
                    },
                    {
                        "name": "Get Analysis Status",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/mood/job/{{job_id}}",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "mood", "job", "{{job_id}}"],
                            },
                        },
                    },
                    {
                        "name": "Get Latest Report",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/api/v1/mood/latest-report",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "mood", "latest-report"],
                            },
                        },
                    },
                    {
                        "name": "Analyze From Scrapper",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "models": ["mistral-large-3:675b-cloud"],
                                    "batch_size": 5,
                                }),
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/mood/analyze-from-scrapper",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "mood", "analyze-from-scrapper"],
                            },
                        },
                    },
                ],
            },
        ],
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
            },
            {
                "key": "job_id",
                "value": "job-id-here",
            },
        ],
    }


if __name__ == "__main__":
    collection = generate_postman_collection()
    with open("postman_collection.json", "w") as f:
        json.dump(collection, f, indent=2)
    print("Postman collection generated: postman_collection.json")
