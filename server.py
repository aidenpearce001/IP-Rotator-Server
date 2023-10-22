from fastapi import FastAPI, HTTPException, Query
import requests
from requests_ip_rotator import ApiGateway

app = FastAPI()

def get_api_gateway_for_host(host: str):
    if host not in api_gateway_instances:
        api_gateway_instances[host] = ApiGateway(host)
    return api_gateway_instances[host]

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down. ApiGateway instances were created for the following hosts:")
    for host in api_gateway_instances.keys():
        print(host.shutdown())

@app.get("/proxy")
def proxy_request(target_url: str = Query(..., alias="target-url")):
    host = target_url.split("//")[1].split("/")[0]
    try:
        api_gateway = get_api_gateway_for_host(host)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        session = api_gateway.get_http_session()
        response = session.get(target_url)
        return {"status_code": response.status_code, "content": response.text}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to make a request")