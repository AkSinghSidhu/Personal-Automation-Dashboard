from .file_tools import validate_file_path
import zipfile
from pathlib import Path


def validate_files_list(files_list):
    files = []
    for file in files_list:
        try:
            file = validate_file_path(file)
            files.append(file)
        except FileNotFoundError:
            continue
        except PermissionError:
            continue
        except (ValueError, OSError) as e:
            continue
    return files

def compress_to_zip(files_to_compress, output_path = "files.zip"):
    files_to_zip = validate_files_list(files_to_compress)
    if files_to_zip:
        Path(output_path).parent.mkdir(parents = True, exist_ok = True)
        with zipfile.ZipFile(output_path, "w", compression = zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_zip:
                zipf.write(file, arcname = Path(file.parent.name) / file.name)
        return output_path
    else:
        raise ValueError("No valid files were found to compress.")