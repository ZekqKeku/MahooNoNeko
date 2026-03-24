import os
import sys
import json
import nanoid
import inspect
import datetime
import importlib
import subprocess

class Requirements:
    def __init__(self, txt_file="requirements.txt"):
        if os.path.exists('/.dockerenv'):
            return

        requirements_path = txt_file

        if os.path.exists(requirements_path):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            except subprocess.CalledProcessError:
                print("Error: Failed to install requirements from requirements.txt")
        else:
            print("Warning: requirements.txt not found")

class ConfigReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config_data = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Config file not found: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_bot_token(self):
        return self.config_data.get("bot", {}).get("token", "")

    def get_super_users(self):
        return self.config_data.get("discord", {}).get("super_users", "")

    def get_pixeldrain_api(self):
        return self.config_data.get("api", {}).get("pixeldrain", {}).get("key", "")

    def get_pixeldrain_direct_link(self):
        return self.config_data.get("api", {}).get("pixeldrain", {}).get("direct_link", "")

    def get_pixeldrain_delete_after(self):
        return self.config_data.get("api", {}).get("pixeldrain", {}).get("delete_after", "")

    def get_pixeldrain_max_file_size(self):
        return self.config_data.get("api", {}).get("pixeldrain", {}).get("max_file_size", "")

    def get_pixeldrain_max_file_length(self):
        return self.config_data.get("api", {}).get("pixeldrain", {}).get("max_file_length", "")

class Loader:
    def __init__(self, payload: dict[str, any], folder="cogs"):
        self.payload = payload
        self.client = payload.get("client")
        self.folder = folder

        if not os.path.exists(self.folder):
            print(f"Warning: Folder {self.folder} not found.")
            return

        for filename in os.listdir(self.folder):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"{self.folder}.{filename[:-3]}"
                class_name = "N/A"

                base_name = filename[:-3]
                pascal_case_name = "".join(word.capitalize() for word in base_name.split("_"))
                cog_class_name = f"{pascal_case_name}Cog"
                standard_class_name = pascal_case_name

                try:
                    module = importlib.import_module(module_name)

                    if hasattr(module, cog_class_name):
                        class_name = cog_class_name
                        cog_class = getattr(module, cog_class_name)
                    elif hasattr(module, standard_class_name):
                        class_name = standard_class_name
                        cog_class = getattr(module, standard_class_name)
                    else:
                        print(f"\n > Failed to load: {module_name}: Class not found.\n")
                        continue

                    sig = inspect.signature(cog_class.__init__)
                    params = list(sig.parameters)[1:]
                    args_map = {
                        "client": self.payload.get('client'),
                        "config": self.payload.get('config'),
                        "pixeldrain": self.payload.get('pixeldrain'),
                        "downloader": self.payload.get('downloader'),
                        "database": self.payload.get('database')
                    }
                    args = [args_map[p] for p in params if p in args_map]

                    cog_instance = cog_class(*args)
                    self.client.add_cog(cog_instance)
                    print(f"Loaded: {class_name}")

                except Exception as e:
                    print(f"\n > Failed to load {module_name} ({class_name}): {e}\n")

class Utils:
    @staticmethod
    def random_name(size: int = 4, parts: int = 5, alphabet: str = None):
        if alphabet is None:
            alphabet = "abcdefghijklmnopqrstuvwxyz"
        return "-".join([nanoid.generate(alphabet, size=size) for _ in range(parts)])

    @staticmethod
    def zero_num(number: int, _len: int = 2):
        return str(number).zfill(_len)

    @staticmethod
    def short_year(year):
        year_str = str(year)
        base = str(datetime.date.today().year)
        prefix_len = len(base) - len(year_str)
        if prefix_len < 0:
            return year_str
        return base[:prefix_len] + year_str

class Lists:
    @staticmethod
    def list_common(data: list[list]):
        if not data:
            return []

        first_list = data[0]
        other_sets = [set(sublist) for sublist in data[1:]]

        return [
            item for item in first_list
            if all(item in s for s in other_sets)
        ]