#!/usr/bin/env python3
"""
DEPRECATED: This script was used to generate the initial bounty-board.txt
from source datasets. The bounty board is now maintained directly.

For current operations, use:
- check_cleared_bounties.py - Check and remove cleared packages
- generate_frontend_data.py - Generate static HTML dashboard
"""

from pathlib import Path

def normalize_package_name(name):
    """Normalize package name for comparison"""
    return name.lower().replace('_', '-').replace('.', '-').strip()

def read_package_list(filepath):
    """Read a package list file and return normalized set and original names dict"""
    packages = []
    normalized_to_original = {}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                packages.append(line)
                normalized = normalize_package_name(line)
                if normalized not in normalized_to_original:
                    normalized_to_original[normalized] = line

    return set(normalized_to_original.keys()), normalized_to_original, packages

def main():
    # Read both files
    exploit_path = Path('bounty-board/exploit_int_packages.txt')
    lw_path = Path('bounty-board/lw_prios_valid.txt')

    print("Reading package lists...")
    exploit_norm, exploit_orig, exploit_list = read_package_list(exploit_path)
    lw_norm, lw_orig, lw_list = read_package_list(lw_path)

    print(f"Exploit interest packages: {len(exploit_list)}")
    print(f"Lightwell valid packages: {len(lw_list)}")

    # Find intersection
    intersection_norm = exploit_norm & lw_norm

    print(f"\n=== INTERSECTION ANALYSIS ===")
    print(f"Packages in both lists: {len(intersection_norm)}")
    print(f"Packages only in exploit_int: {len(exploit_norm - lw_norm)}")
    print(f"Packages only in lw_prios_valid: {len(lw_norm - exploit_norm)}")

    # Get original names for intersection
    intersection_packages = []
    for norm in sorted(intersection_norm):
        # Prefer the exploit_int original name
        orig = exploit_orig.get(norm, lw_orig.get(norm))
        intersection_packages.append(orig)

    print(f"\n=== PACKAGES IN BOTH LISTS ===")
    for pkg in intersection_packages:
        print(f"  {pkg}")

    # Create combined list: intersection first, then unique from each list
    only_exploit = exploit_norm - lw_norm
    only_lw = lw_norm - exploit_norm

    # Get original names for unique packages
    only_exploit_packages = [exploit_orig[norm] for norm in sorted(only_exploit)]
    only_lw_packages = [lw_orig[norm] for norm in sorted(only_lw)]

    # Combine: intersection + exploit-only + lw-only
    combined = intersection_packages + only_exploit_packages + only_lw_packages

    # Write to bounty-board.txt
    output_path = Path('bounty-board/bounty-board.txt')
    with open(output_path, 'w') as f:
        for pkg in combined:
            f.write(f"{pkg}\n")

    print(f"\n=== OUTPUT ===")
    print(f"Created {output_path}")
    print(f"Total packages: {len(combined)}")
    print(f"  - In both lists (high priority): {len(intersection_packages)}")
    print(f"  - Only in exploit_int: {len(only_exploit_packages)}")
    print(f"  - Only in lw_prios_valid: {len(only_lw_packages)}")

    # Create summary file
    summary_path = Path('bounty-board/summary.txt')
    with open(summary_path, 'w') as f:
        f.write("Bounty Board Summary\n")
        f.write("===================\n\n")
        f.write(f"Source Files:\n")
        f.write(f"  - exploit_int_packages.txt: {len(exploit_list)} packages\n")
        f.write(f"  - lw_prios_valid.txt: {len(lw_list)} packages\n\n")
        f.write(f"Intersection Analysis:\n")
        f.write(f"  - Packages in BOTH lists: {len(intersection_packages)}\n")
        f.write(f"  - Packages only in exploit_int: {len(only_exploit_packages)}\n")
        f.write(f"  - Packages only in lw_prios_valid: {len(only_lw_packages)}\n\n")
        f.write(f"Output File Structure (bounty-board.txt):\n")
        f.write(f"  Lines 1-{len(intersection_packages)}: Packages in BOTH lists (highest priority)\n")
        f.write(f"  Lines {len(intersection_packages)+1}-{len(intersection_packages)+len(only_exploit_packages)}: Exploit interest only\n")
        f.write(f"  Lines {len(intersection_packages)+len(only_exploit_packages)+1}-{len(combined)}: Lightwell priority only\n\n")
        f.write(f"Packages in BOTH lists (intersection):\n")
        for pkg in intersection_packages:
            f.write(f"  - {pkg}\n")

    print(f"Created {summary_path}")

if __name__ == '__main__':
    main()
