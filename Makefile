initial-setup:
	poetry install --no-root
	poetry run python3 src/setup/download_data.py
	poetry run python3 src/setup/test_bird.py

run-ollama:
	cd src/agents && docker-compose up -d
	docker exec -it ollama ollama run sqlcoder:7b
 