
import shutil
import os
import re
import glob
import yaml
import json
import pathlib


class NoHeadlineFound(Exception): pass
class NoIndexFile(Exception): pass
class EntryNotFound(Exception): pass


class PathSettings(object):
    mkdocs_yml_file: str = "./mkdocs.yml"
    iris_path_prefix: str =  "/Users/myself/iris-drive/iris-toolbox"
    docs_path_prefix: str = "source"
    headlines_file = "./headlines.yml"
    headlines = dict()
    navigation_template_file = "./navigation-template.yml"
    navigation_file = "./navigation.yml"
    navigation = ""
    higher_level_folders = [
        ["StructuralModeling", "structural-modeling"],
        ["TimeSeriesModeling", "time-series-modeling"],
        ["DataManagement", "data-management"],
        ["Reporting", "reporting"],
        ["Statistics", "statistics-utilities"],
        ["Statistics/+distribution", "statistics-utilities/distribution"]
    ]
    extras: list[str] = ["stylesheets", "images", "javascripts"]

    @classmethod
    def create_higher_level_folders(cls):
        for i in cls.higher_level_folders:
            dir_to_create = os.path.join(PathSettings.docs_path_prefix, i[1])
            print(dir_to_create)
            pathlib.Path(dir_to_create).mkdir(parents=True)
            shutil.copyfile(
                os.path.join(PathSettings.iris_path_prefix, i[0], "index.md"),
                os.path.join(PathSettings.docs_path_prefix, i[1], "index.md"),
            )

    @classmethod
    def load_navigation_template(cls):
        with open(cls.navigation_template_file, "r") as fid:
            cls.navigation = fid.read()

    @classmethod
    def write_navigation(cls):
        with open(cls.navigation_file, "w") as fid:
            fid.write(cls.navigation)

    @classmethod
    def create_fresh_folders(cls) -> None:
        for f in [cls.docs_path_prefix]:
            if os.path.isdir(f):
                shutil.rmtree(f)
            pathlib.Path(f).mkdir(parents=True)

        # Assets to be copied over to source folder
        for x in cls.extras:
            shutil.copytree(x, os.path.join(PathSettings.docs_path_prefix, x))

    @classmethod
    def dump_headlines(cls) -> None:
        with open(cls.headlines_file, "w") as fid:
            yaml.dump({"extra": cls.headlines}, fid, indent=4)

    @classmethod
    def insert_in_navigation(cls, name, insert):
        insert = json.dumps(insert)
        (cls.navigation, num) = re.subn(
            f"(-[ ]*{re.escape(name)}[ ]*:).*",
            r"\1 " + insert,
            cls.navigation,
        )
        if num == 0:
            raise EntryNotFound(name)


class Topic(object):
    def __init__(self, nav_name, nav_folder, iris_path):
        self.nav_name: str = nav_name
        self.nav_folder: str = nav_folder
        self.iris_path: str = iris_path
        self.md_files: list[str] = list()
        self.headlines: dict[str, str] = dict()
        self.navigation: list[dict[str, str]] = list()

    def get_within_docs_path(self, *args) -> str:
        return os.path.join(*self.nav_folder, *args)

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
        if self.nav_folder[-1] != ".":
            pathlib.Path(self.get_docs_path()).mkdir(parents=True)

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
            self.headlines["_" + filename_no_ext] = ma.group(0).strip();

    def populate_navigation(self) -> None:
        self.navigation = list()
        self.navigation.append({"Introduction": self.get_within_docs_path("index.md")})
        for f in self.md_files:
            if f=="index.md":
                continue
            self.navigation.append({f.removesuffix(".md"): self.get_within_docs_path(f)})

    def add_to_headlines(self) -> None:
        headlines_prefix = self.nav_folder[-1]
        PathSettings.headlines[headlines_prefix] = self.headlines

    def add_to_navigation(self) -> None:
        PathSettings.insert_in_navigation(self.nav_name, self.navigation)


PathSettings.create_fresh_folders()
PathSettings.create_higher_level_folders()
PathSettings.load_navigation_template()

topics = [
    Topic("Home", ["."], "."),

    Topic("Model source file language", ["structural-modeling", "slang"], "StructuralModeling/+slang"),
    Topic("Models", ["structural-modeling", "model"], "StructuralModeling/@Model"),
    Topic("Simulation plans", ["structural-modeling", "plan"], "StructuralModeling/@Plan"),
    Topic("Explanatory equations", ["structural-modeling", "explanatory"], "StructuralModeling/@Explanatory"),
    Topic("Linear systems", ["structural-modeling", "linear"], "StructuralModeling/@LinearSystem"),

    Topic("Vector autoregressions", ["time-series-modeling", "var"], "TimeSeriesModeling/@VAR"),
    Topic("Structural VARs", ["time-series-modeling", "svar"], "TimeSeriesModeling/@SVAR"),
    Topic("Panel VARs", ["time-series-modeling", "panel"], "TimeSeriesModeling/@PanelVAR"),
    Topic("Dynamic factor models", ["time-series-modeling", "dfm"], "TimeSeriesModeling/@DFM"),
    Topic("Estimation with prior dummies", ["time-series-modeling", "dummy"], "TimeSeriesModeling/+BVAR"),

    Topic("Dates", ["data-management", "dates"], "DataManagement/@Dater"),
    Topic("Time series", ["data-management", "series"], "DataManagement/@Series"),
    Topic("Databanks", ["data-management", "databank"], "DataManagement/+databank"),
    Topic("Interface to [IMF Data Portal]", ["data-management", "imf"], "DataManagement/+databank/+fromIMF"),
    Topic("Interface to [X13-Arima]", ["data-management", "x13"], "DataManagement/+x13"),

    Topic("Databank chartpacks", ["reporting", "chartpack"], "DataManagement/+databank/@Chartpack"),
    Topic("Interface to [rephrase.js]", ["reporting", "rephrase"], "Plugins/+rephrase"),

    Topic("Beta distribution", ["statistics-utilities", "distribution", "beta"], "Statistics/+distribution/@Beta"),
    Topic("Gamma distribution", ["statistics-utilities", "distribution", "gamma"], "Statistics/+distribution/@Gamma"),
]

for t in topics:
    print("-"*20 + t.nav_name + "-"*20)
    t.copy_md_files()
    print(*t.md_files, sep="\n")

    if t.nav_name=="Home":
        continue

    t.populate_headlines()
    t.populate_navigation()
    t.add_to_navigation()
    t.add_to_headlines()

PathSettings.dump_headlines()
PathSettings.write_navigation()

os.system("cat mkdocs-template.yml navigation.yml > mkdocs.yml");
 
