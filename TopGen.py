import json
import os
import pythoncom
import win32com.client

# Load the movie information from the JSON file
with open("2023top250_movies.json", "r", encoding="utf-8") as f:
    movies = json.load(f)

# Extract all the 番号 and their rankings
codes = {movie["title"].split()[0]: movie for movie in movies}
print(codes)
# Define the directories to search
directories = ["O:\\"]

# Cache to store already found files for each 番号
cache_file = "file_search_cache.json"

# Load cache if it exists
if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        found_files = json.load(f)
else:
    found_files = {code: [] for code in codes}

# Function to save cache
def save_cache():
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(found_files, f, ensure_ascii=False, indent=4)

# Function to create a shortcut
def create_shortcut(target, shortcut_path, description):
    pythoncom.CoInitialize()  # Initialize COM library
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.Description = description
    shortcut.save()

# Function to search for files containing the 番号
def search_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            for code, movie in codes.items():
                try:
                    if code in file and file_path not in found_files[code]:
                        found_files[code].append(file_path)
                except:
                    found_files[code] =[]

        # Save cache periodically to avoid data loss
        if sum(len(paths) for paths in found_files.values()) % 100 == 0:
            save_cache()

for directory in directories:
    search_files(directory)
save_cache()

i = 0
for code, paths in found_files.items():
    for path in paths:
        i += 1
        print(f"番号: {code}, 文件路径: {path}")
        # Create a shortcut on the desktop
        desktop_dir = "C:\\Users\\Chen\\Desktop\\2023TOP250"
        if not os.path.exists(desktop_dir):
            os.makedirs(desktop_dir)
        shortcut_name = f"{i}_{code}.lnk"
        shortcut_path = os.path.join(desktop_dir, shortcut_name)
        try:
            create_shortcut(path, shortcut_path, f"Shortcut to {path}")
        except Exception as e:
            print(f"Error creating shortcut for {path}: {e}")

# Print codes that were not found along with their index, ranking and full title
not_found_codes = [code for code, paths in found_files.items() if not paths]
if not_found_codes:
    print("\nNot found codes:")
    for code in not_found_codes:
        movie = codes[code]
        index = movies.index(movie) +1
        print(f"Index: {index}, 番号: {code}, 排名: {movie['ranking']}, 电影全名: {movie['title']}")
else:
    print("\nAll codes were found.")
