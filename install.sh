python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp ./mycelium-healthcheck.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mycelium-healthcheck
systemctl start mycelium-healthcheck
