from .file_tools import validate_directory, get_file_size, get_file_hash, get_partial_file_hash, format_size

def group_files_by_size(path):
    categorized_by_size = {}
    for file in path.rglob("*"):
        if file.is_file():
            try:
                size = get_file_size(file)
                if size not in categorized_by_size:
                    categorized_by_size[size] = []
                categorized_by_size[size].append(file)
            except OSError:
                continue

    return categorized_by_size

def filter_duplicate_candidates(files_by_size):
    candidate_groups = {
        size: files
        for size, files in files_by_size.items()
        if len(files) > 1
    }

    return candidate_groups

def second_pass_duplicate_candidates(candidate_groups):
    new_candidates = {}
    for size in candidate_groups:
        files = candidate_groups[size]
        for file in files:
            try:
                partial_file_hash = get_partial_file_hash(file)
                if partial_file_hash not in new_candidates:
                    new_candidates[partial_file_hash] = []
                new_candidates[partial_file_hash].append(file)
            except OSError:
                continue

    return new_candidates

def group_files_by_hash(candidate_groups):
    categorized_by_hashes = {}
    for hash_value in candidate_groups:
        files = candidate_groups[hash_value]
        for file in files:
            try:
                file_hash = get_file_hash(file)
                if file_hash not in categorized_by_hashes:
                    categorized_by_hashes[file_hash] = []
                categorized_by_hashes[file_hash].append(file)
            except OSError:
                continue

    return categorized_by_hashes

def filter_duplicate_groups(files_by_hash):
    duplicate_groups = {
        file_hash: files
        for file_hash, files in files_by_hash.items()
        if len(files) > 1
    }

    return duplicate_groups

def preview_duplicate_groups(duplicate_files):
    width = 60
    title = "DUPLICATE FILES PREVIEW"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not duplicate_files:
        print("  (No duplicate files found in this folder)")
        print("=" * width)
        return

    total_groups = len(duplicate_files)
    total_redundant_files = 0
    total_wasted_bytes = 0

    for i, files in enumerate(duplicate_files.values(), start=1):
        file_size = get_file_size(files[0])
        wasted_for_group = file_size * (len(files) - 1)
        total_wasted_bytes += wasted_for_group
        total_redundant_files += len(files) - 1

        print(f"\n[Group {i}] - {format_size(file_size)} each ({len(files)} identical files):")
        for file in files:
            print(f"  • {file}")

    print("\n" + "-" * width)
    print(f"Duplicate Groups: {total_groups}")
    print(f"Redundant Files:  {total_redundant_files}")
    print(f"Wasted Storage:   {format_size(total_wasted_bytes)}")
    print("=" * width)


def find_duplicate_files(path):
    directory = validate_directory(path)

    grouping_files_by_size = group_files_by_size(directory)
    remove_unique_files = filter_duplicate_candidates(grouping_files_by_size)
    new_candidates = second_pass_duplicate_candidates(remove_unique_files)
    remove_partial_unique = filter_duplicate_candidates(new_candidates)
    grouping_files_by_hash = group_files_by_hash(remove_partial_unique)
    duplicate_files = filter_duplicate_groups(grouping_files_by_hash)

    return duplicate_files

if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    duplicate_files = find_duplicate_files(folder_path)
    preview_duplicate_groups(duplicate_files)
