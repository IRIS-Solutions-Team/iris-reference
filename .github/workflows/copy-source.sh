
root=$(pwd)
echo $root

cd $root/iris-reference

if [[ -d source/ ]]; then
    rm -rf source/
fi

mkdir source/

cd $root/iris-toolbox/

gfind . -name '*.md' -o -name '.pages' \
    | gxargs gcp --parents -t $root/iris-reference/source/

cd $root/iris-reference

gmv ./source/README.md ./source/index.md

gcp -r extra source/extra

tree -a source/ -P index.md -P .pages

cd $root


