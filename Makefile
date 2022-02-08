sdist:
	rm -f dist/*
	python setup.py sdist

README.rst: README.md
	pandoc --from=gfm --to=rst -o README.rst README.md

pypi: README.rst sdist
	python setup.py clean
	twine upload --repository pypi dist/*

pypitest: README.rst sdist
	python setup.py clean
	twine upload --repository pypitest dist/*

test:
	python -m unittest discover -v

coverage:
	coverage run -m unittest discover
	coverage report

coverage_missing:
	coverage run -m unittest discover
	coverage report -m

