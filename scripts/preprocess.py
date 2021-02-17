
import shutil
import os
import re
import glob
import json


class NoHeadlineFound(Exception):
    pass


class NoIndexFile(Exception):
    pass


class PathSettings(object):
    mkdocs_yml_file: str = "./mkdocs.yml"
    iris_path_prefix: str =  "/Users/myself/iris-drive/iris-toolbox"
    docs_path_prefix: str = "source"
    headlines_file = "./headlines.yml"
    extras: list[str] = ["stylesheets", "images"]

    @classmethod
    def create_fresh_folders(cls) -> None:
        for f in [cls.docs_path_prefix]:
            if os.path.isdir(f):
                shutil.rmtree(f)
            os.mkdir(f)

        # Assets to be copied over to source folder
        for x in cls.extras:
            shutil.copytree(x, os.path.join(PathSettings.docs_path_prefix, x))

    @classmethod
    def write_headlines(cls, headlines) -> None:
        with open(cls.headlines_file, "w") as fid:
            json.dump(headlines, fid, indent=4)


class Topic(object):
    def __init__(self, nav_name, nav_folder, iris_path):
        self.nav_name: str = nav_name
        self.nav_folder: str = nav_folder
        self.iris_path: str = iris_path
        self.md_files: list[str] = list()
        self.headlines: dict[str, str] = dict()
        self.navigation: list[dict[str, str]] = list()

    def get_within_docs_path(self, *args) -> str:
        return os.path.join(self.nav_folder, *args)

    def get_docs_path(self, *args) -> str:
        return os.path.join(PathSettings.docs_path_prefix, self.get_within_docs_path(*args))

    def get_iris_path(self, *args) -> str:
        return os.path.join(PathSettings.iris_path_prefix, self.iris_path, *args)

    def copy_md_files(self) -> None:
        # Get the list of all *.md files in the IrisT topic folder, sort
        # alphabetically and verify that index.md exists
        self.md_files = shutil.fnmatch.filter(
                os.listdir(self.get_iris_path()),
                "*.md",
        )
        if "index.md" not in self.md_files:
            raise NoIndexFile(self.get_iris_path())

        if "README.md" in self.md_files:
            self.md_files.remove("README.md")

        self.md_files.sort()
        self.md_files.remove("index.md")
        self.md_files.insert(0, "index.md")

        # Create a docs topic folder and copy all the *.md files to there
        if self.nav_folder != ".":
            os.mkdir(self.get_docs_path())

        for f in self.md_files:
            shutil.copyfile(self.get_iris_path(f), self.get_docs_path(f))

    def populate_headlines(self) -> None:
        self.headlines = dict()
        for f in self.md_files:
            if f=="index.md":
                continue
            with open(self.get_docs_path(f)) as fid:
                file_content = fid.read()
            if (ma := re.search("(?<=\{==).*(?===\})", file_content)) is None:
                raise NoHeadlineFound(self.get_iris_path(f))
            filename_no_ext = f;
            filename_no_ext = filename_no_ext.removesuffix(".md")
            self.headlines[filename_no_ext] = ma.group(0).strip();

    def populate_navigation(self) -> None:
        self.navigation = list()
        self.navigation.append({"Introduction": self.get_within_docs_path("index.md")})
        for f in self.md_files:
            if f=="index.md":
                continue
            self.navigation.append({f.removesuffix(".md"): self.get_within_docs_path(f)})

    def add_to_headlines(self, headlines: dict[str, dict]) -> None:
        headlines["extra"][self.nav_folder] = self.headlines

    def write_navigation(self) -> None:
        navigation_json_string = json.dumps(self.navigation);
        with open(PathSettings.mkdocs_yml_file, "r") as fid:
            mkdocs = fid.read()
        mkdocs = re.sub(
                f"^( *- {self.nav_name}: ).*",
                r"\1 " + navigation_json_string,
                mkdocs,
                count=1, flags=re.MULTILINE,
        )
        with open(PathSettings.mkdocs_yml_file, "w") as fid:
            fid.write(mkdocs)


PathSettings.create_fresh_folders()

topics = [
        Topic("Home", ".", "."),
        Topic("Dates", "dates", "DataManagement/@Dater"),
        Topic("Databanks", "databank", "DataManagement/+databank"),
        Topic("Databank Chartpacks", "chartpack", "DataManagement/+databank/@Chartpack"),
]

headlines = {"extra": dict()}

for t in topics:
    print("-"*20 + t.nav_name + "-"*20)
    t.copy_md_files()
    print(*t.md_files, sep="\n")

    if t.nav_name=="Home":
        continue

    t.populate_headlines()
    t.populate_navigation()
    t.write_navigation()
    t.add_to_headlines(headlines)


PathSettings.write_headlines(headlines)

