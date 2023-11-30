import os
from requests import post
from flask import Flask, request, abort
import random
import logging

app = Flask("mycelium-healthcheck")

# Configure Flask logging
app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
app.logger.addHandler(handler)

def is_eth_endpoint_healthy(url):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 5
    }

    headers = {
        "Content-Type": "application/json"
    }

    intermediate_response = post(url, headers=headers, json=payload)

    if intermediate_response.status_code != 200:
        return {"is_up": False, "reason": intermediate_response.content}, intermediate_response.status_code
    
    intermediate_response_json = intermediate_response.json()

    if "error" in intermediate_response_json:
        return {"is_up": False, "reason": intermediate_response.content}, 500
    
    return {"is_up": True}, 200

@app.route("/up")
def is_fleet_healthy():
    url = "https://api.mycelium.calibration.node.glif.io/"
    return is_eth_endpoint_healthy(url)

@app.route('/health')
def is_local_edpoint_healthy():
    url = "http://localhost:8545/"
    return is_eth_endpoint_healthy(url)
