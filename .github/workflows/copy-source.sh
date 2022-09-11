

cd iris-reference

if [[ -d source/ ]]; then
    rm -rf source/
fi

mkdir source

cd ../iris-toolbox

find . -name '*.md' -o -name '.pages' \
    | xargs cp --parents -t ../iris-reference/source/

cd ../iris-reference

mv ./source/README.md ./source/index.md

cp -r ./extra ./source/extra

tree -a ./source/ 

cd ..


