cd ..

pdoc3 examples scenariogeneration --html -o generated --force

pdoc3 docu/for_documentation.py --html -o generated --force

rm *.xo*

cd generated
mv for_documentation.html index.html

sed -i "s+Module <code>for_documentation</code>+Welcome to scenariogeneration+" index.html
sed -i "s+for_documentation API documentation+Welcome to scenariogeneration+" index.html

cd ../docu