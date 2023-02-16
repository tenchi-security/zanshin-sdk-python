README.rst: README.md
	pandoc --from=gfm --to=rst -o README.rst README.md

lint:
	flake8 zanshinsdk --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

test:
	poetry run python -m unittest discover -v

coverage:
	poetry run coverage run -m unittest discover
	poetry run coverage report

coverage_missing:
	poetry run coverage run -m unittest discover
	poetry run coverage report -m

