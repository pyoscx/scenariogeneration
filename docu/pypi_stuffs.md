## update documentation
1.
-change version in setup.py
(both in version and download_url)

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
python setup.py sdist

7.
twine upload dist/*


## update documentation
1.
run ./generate_documentation.sh

2.
cp -rf output/scenariogeneration/* ../pyoscx.github.io

3. commit and push
