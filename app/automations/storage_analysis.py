from .file_tools import validate_directory, get_file_size, format_size
from .file_categories import get_file_category

def get_category_distribution(path):
    directory = validate_directory(path)
    distribution = {}

    for item in directory.rglob("*"):
        try:
            if item.is_file():
                category = get_file_category(item) or "Uncategorized"
                size = get_file_size(item)

                if category not in distribution:
                    distribution[category] = {"count": 0, "size": 0}

                distribution[category]["count"] += 1
                distribution[category]["size"] += size
        except OSError:
            continue

    return distribution

def preview_category_distribution(distribution):
    width = 60
    title = "STORAGE ANALYSIS BY CATEGORY"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not distribution:
        print("  (No files found)")
        print("=" * width)
        return

    total_files = sum(cat["count"] for cat in distribution.values())
    total_size = sum(cat["size"] for cat in distribution.values())

    sorted_categories = sorted(distribution.items(), key=lambda x: x[1]["size"], reverse=True)

    print(f"\n{'Category':<20} {'Files':>6} {'Size':>12} {'%':>6}")
    print("-" * width)

    for category, data in sorted_categories:
        percentage = (data["size"] / total_size * 100) if total_size > 0 else 0
        print(f"  {category:<18} {data['count']:>6} {format_size(data['size']):>12} {percentage:>5.1f}%")

    print("-" * width)
    print(f"  {'Total':<18} {total_files:>6} {format_size(total_size):>12} {'100.0%':>6}")
    print("=" * width)

def get_largest_files(path, limit=10):
    directory = validate_directory(path)
    large_files = []

    for file in directory.rglob("*"):
        try:
            if file.is_file():
                size = get_file_size(file)
                large_files.append({
                    "file": file,
                    "size": size
                })
        except OSError:
            continue

    files_sorted_by_size = sorted(large_files, key=lambda item: item["size"], reverse=True)
    top_largest_files = files_sorted_by_size[:limit]

    return top_largest_files

if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    distribution = get_category_distribution(folder_path)
    preview_category_distribution(distribution)