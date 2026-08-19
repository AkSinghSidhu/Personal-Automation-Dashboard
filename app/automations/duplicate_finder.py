from .file_tools import validate_directory, get_file_size, get_file_hash

def group_files_by_size(path):
    
    
    categorized_by_size = {}
    for file in path.rglob("*"):
        if file.is_file():
            size = get_file_size(file)
            if size not in categorized_by_size:
                categorized_by_size[size] = []

            categorized_by_size[size].append(file)

    return categorized_by_size

def filter_duplicate_candidates(files_by_size):
    candidate_groups = {
        size: files
        for size, files in files_by_size.items()
        if len(files) > 1
    }

    return candidate_groups

def group_files_by_hash(candidate_groups):

    categorized_by_hashes = {}
    for size in candidate_groups:
        files = candidate_groups[size]
        for file in files:
            file_hash = get_file_hash(file)
            if file_hash not in categorized_by_hashes:
                categorized_by_hashes[file_hash] = []

            categorized_by_hashes[file_hash].append(file)

    return categorized_by_hashes

def filter_duplicate_groups(files_by_hash):
    duplicate_groups = {
        file_hash: files
        for file_hash, files in files_by_hash.items()
        if len(files) > 1
    }

    return duplicate_groups

def find_duplicate_files(path):
    directory = validate_directory(path)

    grouping_files_by_size = group_files_by_size(directory)
    remove_unique_files = filter_duplicate_candidates(grouping_files_by_size)
    grouping_files_by_hash = group_files_by_hash(remove_unique_files)
    duplicate_files = filter_duplicate_groups(grouping_files_by_hash)

    return duplicate_files

if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    duplicate_files = find_duplicate_files(folder_path)