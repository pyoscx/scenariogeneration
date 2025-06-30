## Release to PyPI

1.  
Change version in `pyproject.toml`  
(update the `version = "..."` field under `[project]`)

Add release notes in file `release_notes.md` and save the changes.

2.  
Then add the files, commit and push:
```sh
git add -u
git commit -m "prep release"
git push
```

3. 
Tag the release:
```sh
git tag -a "v0.15.X" -m "Version 0.15.X"
```

4. 
Push the tags:
```sh
git push --tags
```

5. 
Remove old build artifacts:
```sh
rm -rf dist
```
6.  
Ensure the `build` package is installed. If not, install it with:
```sh
pip install build
```
Then build the artifacts:
```sh
python3 -m build
```

7. 
Upload the artifacts:
```sh
twine upload dist/*
```


## update documentation
1. 
Ensure the `pdoc3` package is installed. 
If not install it with:
```sh
pip install pdoc3
```
Generate the documentation:
```sh
cd docu
./generate_documentation.sh
```

2. 
Make sure you have cloned the sibling repo https://github.com/pyoscx/pyoscx.github.io  
If not clone the sibling repository if you haven't already:
```sh
git clone https://github.com/pyoscx/pyoscx.github.io
``` 

Copy the generated files into the sibling repo:
```sh
cp -rf generated/* ../pyoscx.github.io
```

3. 
Go to the sibling repo with
```sh
cd ../pyoscx.github.io
```

Then add the files, commit and push.
```sh
git add 
commit -m "Your commit message" 
git push
```
