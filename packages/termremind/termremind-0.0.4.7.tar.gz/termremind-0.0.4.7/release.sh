rm -rfv dist/*
python3 setup.py sdist bdist_wheel
twine upload dist/*