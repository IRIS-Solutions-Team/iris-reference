
import os
import re
import json

iris_root = "/Users/myself/iris-drive/iris-toolbox"
table_width = 60

def get_indexed_content(iris_root):
    """
    Walk through the IrisT folder structure and extract the paths to all folders
    that have an index.md file in them, and the list of all *.md files
    in each of these folders
    """
    indexed_folders = []
    md_names = dict()
    for (folder, _, names) in os.walk(iris_root):
        if "index.md" in names:
            indexed_folders.append(folder)
            md_names[folder] = [n for n in names if n.endswith(".md")]
            # for n in md_names[folder]:
            #     file_path = os.path.join(folder, n)
            #     with open(file_path, "r") as fid:
            #         x = fid.read()
            #     x = re.sub(r"^#\s+`(.*?)`", r"# \1", x)
            #     with open(file_path, "w+") as fid:
            #         fid.write(x)
    return indexed_folders, md_names



class Tracker():
    def __init__(self):
        self.files = list()

    def replace_h1(self, match, folder):

        def extract_h1(file_name):
            with open(file_name, "r") as fid: 
                file_content = fid.read()
            ma = re.search(r"{==(.*?)==}", file_content)
            if ma is None:
                raise NoDescriptionFound(file_name)
            return ma.group(1).strip()

        # Extract the file name and remove leading ( and trailing ) from it
        file_name = match.group(2)
        if file_name.startswith("("):
            file_name = file_name[1:]
        if file_name.endswith(")"):
            file_name = file_name[:-1] 

        self.files.append(file_name)
        file_path = os.path.join(folder, file_name)
        h1 = extract_h1(file_path)
        return (match.group(1) + match.group(2)).ljust(table_width) + " | " + h1



def main():
    info = dict()
    folders, md_names = get_indexed_content(iris_root)
    for folder in folders:
        info[folder] = dict()
        tracker = Tracker()
        with open(os.path.join(folder, "index.md"), "r") as fid:
            index_file = fid.read()
            (index_file, _) = re.subn( 
                r"^\|?\s*(\[.*?\])(\(.*?\))\s*\|(.*)$", 
                lambda match: tracker.replace_h1(match, folder), 
                index_file, flags=re.MULTILINE
            )
        with open(os.path.join(folder, "index.md"), "w+") as fid:
            fid.write(index_file)
        all_md_files = [ x for x in os.listdir(folder) if x.endswith(".md") and x!="index.md" ]
        info[folder]["not_included"] = list(set(all_md_files) - set(tracker.files))
        info[folder]["included"] = tracker.files
    return info



if __name__=="__main__":
    info = main()
    warn = { key:value["not_included"] for key, value in info.items() if value["not_included"] }
    print(json.dumps(warn, indent=5))


