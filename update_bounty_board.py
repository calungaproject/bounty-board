#!/usr/bin/env python3
"""
Update bounty-board.txt by incorporating packages from all dataset files.

This script:
1. Reads all files from datasets/ directory
2. Merges with existing bounty-board.txt
3. Removes duplicates (case-insensitive comparison with normalization)
4. Maintains priority structure:
   - Lines 1-24: HIGH priority (existing)
   - Lines 25-99: MEDIUM priority (existing)
   - Lines 100+: LOW priority (existing + new packages)
"""

from pathlib import Path


def normalize_package_name(name):
    """Normalize package name for comparison."""
    return name.lower().replace('_', '-').replace('.', '-').strip()


def read_package_list(filepath):
    """Read a package list file and return list of packages."""
    packages = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                packages.append(line)
    return packages


def main():
    base_dir = Path(__file__).parent
    bounty_board_path = base_dir / "bounty-board.txt"
    datasets_dir = base_dir / "datasets"

    # Read existing bounty board
    print("Reading existing bounty-board.txt...")
    existing_packages = read_package_list(bounty_board_path)
    original_count = len(existing_packages)
    print(f"  Current packages: {original_count}")

    # Determine priority boundaries in existing list
    # Assume first 24 are HIGH, next 75 are MEDIUM, rest are LOW
    high_priority_end = min(24, original_count)
    medium_priority_end = min(99, original_count)

    high_priority = existing_packages[:high_priority_end]
    medium_priority = existing_packages[high_priority_end:medium_priority_end]
    low_priority = existing_packages[medium_priority_end:]

    print(f"  HIGH priority: {len(high_priority)}")
    print(f"  MEDIUM priority: {len(medium_priority)}")
    print(f"  LOW priority: {len(low_priority)}")

    # Track normalized names to avoid duplicates
    seen_normalized = set()
    for pkg in existing_packages:
        seen_normalized.add(normalize_package_name(pkg))

    # Read all dataset files
    new_packages = []
    dataset_files = sorted(datasets_dir.glob("dataset_*.txt"))

    print(f"\nProcessing {len(dataset_files)} dataset files...")
    for dataset_file in dataset_files:
        print(f"  Reading {dataset_file.name}...")
        packages = read_package_list(dataset_file)
        dataset_new = 0

        for pkg in packages:
            normalized = normalize_package_name(pkg)
            if normalized not in seen_normalized:
                new_packages.append(pkg)
                seen_normalized.add(normalized)
                dataset_new += 1

        print(f"    Total: {len(packages)}, New: {dataset_new}")

    # Sort new packages alphabetically
    new_packages.sort(key=str.lower)

    print(f"\nTotal new packages to add: {len(new_packages)}")

    # Combine: keep existing structure, append new packages to LOW priority
    combined_low_priority = low_priority + new_packages
    final_list = high_priority + medium_priority + combined_low_priority

    print(f"\nFinal bounty board structure:")
    print(f"  Lines 1-{len(high_priority)}: HIGH priority")
    print(f"  Lines {len(high_priority)+1}-{len(high_priority)+len(medium_priority)}: MEDIUM priority")
    print(f"  Lines {len(high_priority)+len(medium_priority)+1}-{len(final_list)}: LOW priority")
    print(f"  Total packages: {len(final_list)}")

    # Write updated bounty board
    with open(bounty_board_path, 'w') as f:
        for pkg in final_list:
            f.write(f"{pkg}\n")

    print(f"\n✓ Updated {bounty_board_path}")
    print(f"  Added {len(new_packages)} new packages")
    print(f"  Total: {original_count} → {len(final_list)} (+{len(final_list) - original_count})")


if __name__ == "__main__":
    main()
