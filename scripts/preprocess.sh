
###########################################################
# List of IrisT folders and their mapping to docs/ folders
unset folders
declare -A folders
declare -A nav_names

folders[.]=${iris}

folders[Dater]=${iris}/DataManagement/@Dater
nav_names[Dater]=Dates

###########################################################


cd $i/iris-reference

# Clean up
grm -rf docs/
grm -rf meta/

# Recreate subfolders
gmkdir docs
gmkdir meta

# Copy extras to docs/
unset extras
declare -a extras
extras=(stylesheets images)
for e in ${extras[@]}; do
    gcp -r $e/ docs/$e/
done

function retrieve_headline_from_docs_file {
    gtr "\n" " " < docs/$1 \
        | ggrep -ohP -m 1 "(?<={==).*(?===})" \
        | gsed "s/^ *//" \
        | gsed "s/ \+/ /g"
}


unset include_yaml
declare -a include_yaml


for f in ${!folders[@]}; do
    echo ============================ $f ============================
    gmkdir -p docs/$f
    gcp -v -t docs/$f ${folders[$f]}/*md

    if test "_$f" == "_."; then
        rm "docs/$f/README.md"
        continue
    fi
    
    # Get sorted list of base names of markdown files (no path), remove .md
    # extensions
    list_of_md_files=($(gbasename -s ".md" docs/$f/*md | sort))

    # Start a new meta/$f.yml file to list the headlines (Matlab H1) for
    # individual md files in this folder; these meta files are referenced
    # from within mkdocs.yml
    echo extra: > meta/$f.yml
    echo "    $f:" >> meta/$f.yml

    # Start a new dictionary that will be included in the nav entry in
    # mkdocs.yml
    unset ordered_nav
    declare -a ordered_nav

    unset nav
    declare -A nav

    ordered_nav+=("Introduction")
    nav[Introduction]="$f/index.md"

    # Cycle over md files in this folder; for each except index
    # do the following:
    # * Populate meta/$f.yml with headlines
    # * Populate nav structure
    for j in ${list_of_md_files[@]}; do
        if test "_$j" == "_index"; then
            continue
        fi

        # Add entry to nav dictionary: e.g.simulate:Model/simulate.md
        ordered_nav+=("$j")
        nav["$j"]="$f/$j.md"

        # Add entry meta/$f.yml
        headline=$( retrieve_headline_from_docs_file $f/$j.md )
        echo "        $j: $headline" >> meta/$f.yml 
    done

    cat meta/$f.yml
    include_yaml+=(meta/$f.yml)

    # Print nav entries as one string representing a dictionary
    # [ {Introduction:index.md},{hh:hh.md},...]
    nav_printed=$( 
        printf "[";
        for key in ${ordered_nav[@]}; do printf "{%s: %s}, " "$key" "${nav[$key]}"; done;
        printf "]";
    )
    # echo $nav_printed
    # Insert nav_printed into mkdocs.yml
    subs="s;- ${nav_names[$f]}:.*;- ${nav_names[$f]}: $nav_printed;"
    echo $subs
    gsed -i "$subs" mkdocs.yml

    echo
    echo
done

# Create subs command for gsed to replace 
# /include_yaml:.*/
# with
# /include_yaml: [xxx/yyy, ...]/
# Use ; as a separator because / is contained in paths
subs=$( IFS=", "; echo "s;include_yaml:.*;include_yaml: [${include_yaml[*]}];" )
# echo $subs

gsed -i "$subs" mkdocs.yml


