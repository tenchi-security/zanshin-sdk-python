sdist:
	rm -f dist/*
	python setup.py sdist

README.rst: README.md
	pandoc --from=gfm --to=rst -o README.rst README.md

pypi: README.rst sdist
	python setup.py clean
	test -n "$(TWINE_REPOSITORY_URL)"  # TWINE_REPOSITORY_URL must be set
	test -n "$(TWINE_USERNAME)"  # TWINE_USERNAME must be set
	test -n "$(TWINE_PASSWORD)"  # TWINE_PASSWORD must be set
	twine upload dist/*

lint:
	flake8 zanshinsdk --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

test:
	python -m unittest discover -v

coverage:
	coverage run -m unittest discover
	coverage report

coverage_missing:
	coverage run -m unittest discover
	coverage report -m

