ETHAPI_HEALTH_URL="http://localhost:1232/health";

ETHAPI_HEALTH_RESPONSE=$(curl --write-out '%{http_code}' --silent --output /dev/null $ETHAPI_HEALTH_URL);

if [ $ETHAPI_HEALTH_RESPONSE -eq "500" ]; then
    docker restart $(docker ps -a --filter "name=ethapi" -q);
fi
