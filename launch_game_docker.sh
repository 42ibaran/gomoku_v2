docker build --file=app/App.Dockerfile -t gomoku_app .
docker build --file=Dockerfile -t gomoku_server .
docker-compose -f docker-compose.yml up
