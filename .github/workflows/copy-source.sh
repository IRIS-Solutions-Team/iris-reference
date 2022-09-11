

cd $GITHUB_WORKSPACE/iris-reference

if [[ -d source/ ]]; then
    rm -rf source/
fi

mkdir $GITHUB_WORKSPACE/iris-reference/source

cd $GITHUB_WORKSPACE/iris-toolbox

find . -name '*.md' -o -name '.pages' \
    | xargs cp --parents -t $GITHUB_WORKSPACE/iris-reference/source/

cd $GITHUB_WORKSPACE/iris-reference

mv ./source/README.md ./source/index.md

cp -r ./extra ./source/extra

tree -a ./source/ 

cd $GITHUB_WORKSPACE


