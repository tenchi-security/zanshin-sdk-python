README.rst: README.md
	pandoc --from=gfm --to=rst -o README.rst README.md

lint:
	poetry run pre-commit run -a

test:
	python -m unittest discover test -p "test_*.py"

coverage:
	poetry run coverage run -m unittest discover
	poetry run coverage report

coverage_missing:
	poetry run coverage run -m unittest discover
	poetry run coverage report -m
