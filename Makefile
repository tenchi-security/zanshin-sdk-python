README.rst: README.md
	pandoc --from=gfm --to=rst -o README.rst README.md

pypi: README.rst
	python setup.py clean
	twine upload --repository pypi dist/*

pypitest: README.rst
	python setup.py clean
	twine upload --repository pypitest dist/*
