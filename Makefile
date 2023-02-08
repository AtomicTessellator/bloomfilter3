FORCE: ;

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -rf .mypy_cache

tests: FORCE
	pytest --cov=bloomfilter3 --cov-report=xml tests

init:
	python -m pip install --upgrade pip wheel
	python -m pip install -r requirements.txt
	python -m pip check

lint:
	isort bloomfilter3
	black bloomfilter3
