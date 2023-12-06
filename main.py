from requests import post
from flask import Flask
import logging
import re
import subprocess

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

def get_current_subnet():
    ipc_config = None
    with open("/home/ubuntu/.ipc/config.toml", "r") as f:
        ipc_config = f.readlines()

    exp = "^id = \"(.*?)\"$"
    subnets = [re.findall(exp, line)[0] for line in ipc_config if "id =" in line]

    return subnets[-1]

@app.route("/topdown")
def get_parent_finality():
    subnet = get_current_subnet()
    cmd = [
        "/home/ubuntu/ipc/target/release/ipc-cli",
        "cross-msg",
        "parent-finality",
        "--subnet",
        f'{subnet}'
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    err_msg = err.decode('utf-8')
    if "ERROR" in err_msg:
        return {"ok": False, "reason": str(err_msg)}, 500

    parent_finality = out.decode('utf-8').replace("\n", "")
    return {"ok": True, "finality": str(parent_finality)}, 200

@app.route("/up")
def is_fleet_healthy():
    url = "https://api.mycelium.calibration.node.glif.io/"
    return is_eth_endpoint_healthy(url)

@app.route('/health')
def is_local_edpoint_healthy():
    url = "http://localhost:8545/"
    return is_eth_endpoint_healthy(url)

if __name__ == "__main__":
    app.run(debug=True)
