## update documentation
1.
-change version in setup.py
(update the `version = "..."` field under `[project]`)

-add release notes


2.
git add -u
git commit -m "prep release"
git push

3.
git tag -a "v0.2.X" -m "Version 0.2.X"

4.
git push --tags

5.
rm -rf dist

6.
python -m build

7.
twine upload dist/*


## update documentation
1.
run ./generate_documentation.sh

2.
cp -rf output/scenariogeneration/* ../pyoscx.github.io

3. commit and push
