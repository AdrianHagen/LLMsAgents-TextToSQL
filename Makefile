initial-setup:
	poetry install --no-root
	poetry run python3 src/setup/download_data.py
	poetry run python3 src/setup/test_bird.py
