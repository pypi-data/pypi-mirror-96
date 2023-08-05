MODULE=imagedata

all:	dist test

test:
	#nosetests3 -v -s tests
	#nosetests3 tests
	tox

dist:
	python3 -m pep517.build .

test_upload:
	twine upload --repository testpypi dist/*

upload:
	twine upload dist/*

git:
	#git tag -a $(call next_patch_ver)
	git push origin master --tags
