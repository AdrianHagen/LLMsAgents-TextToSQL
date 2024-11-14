initial-setup:
	poetry install --no-root
	poetry run python3 setup/download_data.py
	poetry run python3 setup/test_bird.py
