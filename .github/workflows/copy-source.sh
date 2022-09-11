
root=$(pwd)
echo $root

cd $root/iris-reference

if [[ -d source/ ]]; then
    rm -rf source/
fi

mkdir source/

cd $root/iris-toolbox/

find . -name '*.md' -o -name '.pages' \
    | xargs cp --parents -t $root/iris-reference/source/

cd $root/iris-reference

mv ./source/README.md ./source/index.md

cp -r extra source/extra

tree -a source/ -P index.md -P .pages

cd $root


