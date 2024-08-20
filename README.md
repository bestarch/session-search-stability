# Session & Search Stability

## Run the application as a docker image in a specific region  

docker run -p 127.0.0.1:5555:5555 -e REDISHOST=<REDIS_HOST> -e REDISPORT=<REDIS_PORT> -e REDISPASSWORD=<REDIS_PASSWORD> -e REGION=<DEPLOYMENT_REGION> abhishekcoder/session-search-stability

