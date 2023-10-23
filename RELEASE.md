# Release instructions
* Pick a new version number
* Update the version number in `pyproject.toml`
* Update the version number in `docs/conf.py`
```bash
make test regression_test

git add .
git commit

rm -Rd dist
make build

python3 -m twine upload --repository testpypi dist/* --verbose
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps cbpickaxe --force-reinstall

pushd data/main_game_docs
cbpickaxe_generate_docs build
popd
pushd data/mods
cbpickaxe_generate_docs build
popd

export VERSION=v0.1.0
git tag -a $(VERSION)
git push origin $(VERSION)

python3 -m twine upload dist/* --verbose
```
* Create a new release on GitHub