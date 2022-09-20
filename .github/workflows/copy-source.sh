

cd iris-reference
pwd

if [[ -d source/ ]]; then
    rm -rf source/
fi

mkdir source

cd ../iris-toolbox
pwd

find . \( -name '*.md' -o -name '.pages' \) -print \
    | while read -r filename; do cp --parents -t ../iris-reference/source/ "$filename"; done

cd ../iris-reference
pwd

mv ./source/README.md ./source/index.md

cp -r ./extra ./source/extra

#tree -a ./source/ 

cd ..
pwd


