README.rst: README.md
	pandoc --from=gfm --to=rst -o README.rst README.md

lint:
	poetry run pre-commit run -a

test:
	poetry run python -m unittest discover -v

coverage:
	poetry run coverage run -m unittest discover
	poetry run coverage report

coverage_missing:
	poetry run coverage run -m unittest discover
	poetry run coverage report -m

