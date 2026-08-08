from pathlib import Path
from .file_tools import validate_directory

FILE_CATEGORIES = {
    "Images": {
        ".jpg", ".jpeg", ".jpe", ".jfif",
        ".png", ".gif", ".bmp", ".webp",
        ".tif", ".tiff", ".ico", ".svg",
        ".heic", ".heif", ".avif",
        ".raw", ".cr2", ".cr3", ".nef",
        ".arw", ".dng", ".orf", ".rw2",
        ".psd", ".xcf", ".ai", ".eps"
    },

    "Videos": {
        ".mp4", ".m4v", ".mkv", ".mov",
        ".avi", ".wmv", ".flv", ".webm",
        ".mpeg", ".mpg", ".mpe", ".m2v",
        ".ts", ".mts", ".m2ts", ".3gp",
        ".3g2", ".vob", ".ogv", ".rm",
        ".rmvb", ".asf"
    },

    "Audio": {
        ".mp3", ".wav", ".flac", ".aac",
        ".m4a", ".ogg", ".oga", ".opus",
        ".wma", ".aiff", ".aif", ".aifc",
        ".alac", ".ape", ".mid", ".midi",
        ".amr", ".ac3", ".dts", ".mka"
    },

    "Documents": {
        ".pdf",
        ".doc", ".docx", ".docm", ".dot", ".dotx",
        ".odt", ".ott", ".rtf", ".txt",
        ".tex", ".wpd", ".pages",
        ".epub", ".mobi", ".azw", ".azw3",
        ".fb2", ".djvu",
        ".eml", ".msg"
    },

    "Spreadsheets": {
        ".xls", ".xlsx", ".xlsm", ".xlsb",
        ".xlt", ".xltx", ".ods", ".ots",
        ".csv", ".tsv", ".numbers"
    },

    "Presentations": {
        ".ppt", ".pptx", ".pptm",
        ".pot", ".potx", ".pps", ".ppsx",
        ".odp", ".otp", ".key"
    },

    "Archives": {
        ".zip", ".rar", ".7z", ".tar",
        ".gz", ".bz2", ".xz", ".zst",
        ".lz", ".lz4", ".lzma",
        ".tgz", ".tbz", ".txz",
        ".cab", ".arj", ".ace",
        ".jar", ".war", ".ear"
    },

    "Disk Images": {
        ".iso", ".img", ".dmg", ".vhd",
        ".vhdx", ".vmdk", ".vdi", ".qcow",
        ".qcow2", ".ova", ".ovf", ".bin",
        ".cue", ".nrg", ".mdf", ".mds"
    },

    "Executables": {
        ".exe", ".msi", ".msix", ".appx",
        ".deb", ".rpm", ".appimage",
        ".run", ".bin",
        ".com", ".bat", ".cmd",
        ".sh", ".bash", ".zsh",
        ".dll", ".so", ".dylib"
    },

    "Code": {
        ".py", ".pyw",
        ".js", ".jsx", ".mjs", ".cjs",
        ".ts", ".tsx",
        ".java", ".class", ".jar",
        ".c", ".h", ".cc", ".cpp", ".cxx",
        ".hpp", ".cs",
        ".go", ".rs", ".swift", ".kt", ".kts",
        ".php", ".rb", ".pl", ".pm",
        ".lua", ".r", ".R",
        ".dart", ".scala", ".groovy",
        ".hs", ".fs", ".fsx", ".vb",
        ".asm", ".s",
        ".sql",
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        ".vue", ".svelte"
    },

    "Data": {
        ".json", ".jsonl",
        ".xml", ".yaml", ".yml",
        ".toml", ".ini", ".cfg", ".conf",
        ".env",
        ".db", ".sqlite", ".sqlite3",
        ".mdb", ".accdb",
        ".dbf", ".dat"
    },

    "Fonts": {
        ".ttf", ".otf", ".woff", ".woff2",
        ".eot"
    },

    "Subtitles": {
        ".srt", ".vtt", ".ass", ".ssa",
        ".sub", ".sbv"
    },

    "3D": {
        ".obj", ".fbx", ".gltf", ".glb",
        ".stl", ".3ds", ".blend",
        ".dae", ".abc", ".ply",
        ".max", ".ma", ".mb"
    },

    "Design": {
        ".fig", ".sketch", ".xd",
        ".indd", ".indt",
        ".cdr", ".afdesign", ".afphoto",
        ".kra", ".ora"
    },

    "Game Files": {
        ".pak", ".pk3", ".pk4",
        ".wad", ".bsp",
        ".rom", ".nes", ".sfc", ".smc",
        ".gba", ".gb", ".gbc",
        ".nds", ".n64", ".z64",
        ".sav"
    },

    "Torrents": {
        ".torrent"
    },

    "Backups": {
        ".bak", ".backup", ".old",
        ".tmp", ".temp",
        ".swp", ".swo"
    }
}

def create_organization_plan(path):
    directory = validate_directory(path)
    organization_plan = []
    for content in directory.glob("*"):
        if content.is_file():
            file_category = get_file_category(content)
            destination_path = get_file_destination(content, file_category)

            file_info = {
                "file": content,
                "category": file_category,
                "destination": destination_path
            }
            organization_plan.append(file_info)

    return organization_plan
    

def get_file_category(file):
    extension = file.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return None

def get_file_destination(file, category):
    if category is None:
        destination_path = file.parent / file.name
    else:
        destination_path = file.parent / category / file.name

    return destination_path


if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    organization_plan = create_organization_plan(folder_path)
    print(organization_plan)