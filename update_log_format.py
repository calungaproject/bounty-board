#!/usr/bin/env python3
"""
Update cleared-bounties.log to include PR links from calunga-index-prs.json
for entries that don't already have PR links.
"""

import json
import re
from pathlib import Path


def normalize_package_name(name):
    """Normalize package name for comparison"""
    return name.lower().replace('_', '-').replace('.', '-').strip()


def load_pr_data(filepath):
    """Load PR data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def get_pr_link(package_name, pr_data):
    """Get the PR link for a package from the PR data"""
    # Try exact match first
    if package_name in pr_data:
        prs = pr_data[package_name]
        if prs:
            return prs[0].get('link', 'N/A')

    # Try normalized matching
    normalized_pkg = normalize_package_name(package_name)
    for pkg_key, prs in pr_data.items():
        if normalize_package_name(pkg_key) == normalized_pkg and prs:
            return prs[0].get('link', 'N/A')

    return 'N/A'


def update_log_file(log_path, pr_data):
    """Update the log file with PR links"""
    with open(log_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    updated_count = 0

    # Pattern for old format: timestamp | package | Position: X | Priority: Y
    # Pattern for new format: timestamp | package | Position: X | Priority: Y | PR: URL
    old_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([^|]+) \| (Position: \d+) \| (Priority: [^|]+)$')
    new_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([^|]+) \| (Position: \d+) \| (Priority: [^|]+) \| PR: ')

    for line in lines:
        # Check if line matches old format (no PR link)
        old_match = old_pattern.match(line.strip())
        new_match = new_pattern.match(line.strip())

        if old_match and not new_match:
            timestamp = old_match.group(1)
            package = old_match.group(2).strip()
            position = old_match.group(3)
            priority = old_match.group(4).strip()

            # Get PR link
            pr_link = get_pr_link(package, pr_data)

            # Reconstruct line with PR link
            new_line = f"{timestamp} | {package} | {position} | {priority} | PR: {pr_link}\n"
            updated_lines.append(new_line)
            updated_count += 1
            print(f"Updated: {package} -> {pr_link}")
        else:
            # Keep line as-is (comment, header, or already has PR link)
            updated_lines.append(line)

    # Write updated content back
    with open(log_path, 'w') as f:
        f.writelines(updated_lines)

    return updated_count


def main():
    log_path = Path('cleared-bounties.log')
    pr_data_path = Path('calunga-index-prs.json')

    if not log_path.exists():
        print(f"Error: {log_path} not found")
        return

    if not pr_data_path.exists():
        print(f"Error: {pr_data_path} not found")
        return

    print("Loading PR data...")
    pr_data = load_pr_data(pr_data_path)
    print(f"Loaded PR data for {len(pr_data)} packages")

    print("\nUpdating log file...")
    updated_count = update_log_file(log_path, pr_data)

    print(f"\n✓ Updated {updated_count} entries with PR links")
    print(f"✓ Log file updated: {log_path}")


if __name__ == '__main__':
    main()
