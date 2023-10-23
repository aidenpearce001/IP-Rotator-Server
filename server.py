from fastapi import FastAPI, HTTPException, Query
import requests, base64 
from urllib.parse import urlparse
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS

from loguru import logger

app = FastAPI()

api_gateway_instances = {}

def get_api_gateway_for_host(host: str):
    if host not in api_gateway_instances:
        api_gateway_instances[host] = ApiGateway(host, regions=EXTRA_REGIONS,)
    return api_gateway_instances[host]

@app.on_event("shutdown")
def shutdown_event():
    try:    
        for host in api_gateway_instances.keys():
            host.shutdown()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    logger.success("Shutting down. ApiGateway instances were created for the following hosts:")

@app.get("/proxy/")
def proxy_request(target_url: str):
    parsed_url =  urlparse(target_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    try:
        api_gateway = get_api_gateway_for_host(base_url)
        api_gateway.start()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        session = requests.Session()
        session.mount(base_url, api_gateway)
        response = session.get(target_url)

        b64_encode = (response.text).encode("ascii") 
        return b64_encode
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to make a request")
