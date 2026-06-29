#!/usr/bin/env python3
"""
Check if any packages in bounty-board.txt exist in Red Hat trusted libraries.
Filter out found packages and log them as cleared bounties.
"""

import subprocess
import re
import sys
from pathlib import Path
from datetime import datetime

def normalize_package_name(name):
    """Normalize package name for comparison"""
    return name.lower().replace('_', '-').replace('.', '-').strip()

def fetch_trusted_packages():
    """Fetch packages from Red Hat trusted libraries index"""
    print("Fetching Red Hat trusted libraries index...", file=sys.stderr)
    try:
        result = subprocess.run(
            ['curl', '-sL', 'https://packages.redhat.com/trusted-libraries/python'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"Error fetching trusted libraries: {result.stderr}", file=sys.stderr)
            return set()

        # Extract package names from HTML anchor tags
        # Format: <a href="package-name/">package-name</a><br/>
        content = result.stdout
        trusted = set()

        pattern = r'<a href="([^"]+)/">([^<]+)</a>'
        matches = re.findall(pattern, content)

        for href, display in matches:
            pkg_name = href.rstrip('/')
            trusted.add(pkg_name)

        print(f"Found {len(trusted)} packages in trusted libraries", file=sys.stderr)
        return trusted

    except Exception as e:
        print(f"Error fetching trusted libraries: {e}", file=sys.stderr)
        return set()

def read_bounty_board(filepath):
    """Read bounty board and return list of packages (preserving order)"""
    packages = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                packages.append(line)
    return packages

def write_bounty_board(filepath, packages):
    """Write packages back to bounty board file"""
    with open(filepath, 'w') as f:
        for pkg in packages:
            f.write(f"{pkg}\n")

def append_to_cleared_log(log_path, cleared_packages):
    """Append cleared packages to the log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create log file if it doesn't exist
    if not log_path.exists():
        with open(log_path, 'w') as f:
            f.write("# Cleared Bounties Log\n")
            f.write("# Packages that were found in Red Hat trusted libraries and removed from bounty board\n")
            f.write("# Format: YYYY-MM-DD HH:MM:SS | package-name\n\n")

    with open(log_path, 'a') as f:
        f.write(f"# Cleared on {timestamp}\n")
        for pkg_info in cleared_packages:
            f.write(f"{timestamp} | {pkg_info['package']} | Position: {pkg_info['position']} | Priority: {pkg_info['priority']}\n")
        f.write("\n")

def get_priority_level(position):
    """Determine priority level based on position in bounty board"""
    if position <= 24:
        return "HIGH (both lists)"
    elif position <= 99:
        return "MEDIUM (exploit interest)"
    else:
        return "LOW (lightwell priority)"

def main():
    bounty_board_path = Path('bounty-board.txt')
    cleared_log_path = Path('cleared-bounties.log')

    if not bounty_board_path.exists():
        print(f"Error: {bounty_board_path} not found", file=sys.stderr)
        sys.exit(1)

    # Read current bounty board
    print("Reading bounty board...", file=sys.stderr)
    bounty_packages = read_bounty_board(bounty_board_path)
    original_count = len(bounty_packages)
    print(f"Current bounty board: {original_count} packages", file=sys.stderr)

    # Fetch trusted libraries
    trusted = fetch_trusted_packages()
    trusted_normalized = {normalize_package_name(p) for p in trusted}

    # Check for cleared packages
    cleared_packages = []
    remaining_packages = []

    for idx, pkg in enumerate(bounty_packages, 1):
        normalized = normalize_package_name(pkg)

        if normalized in trusted_normalized:
            priority = get_priority_level(idx)
            cleared_info = {
                'package': pkg,
                'position': idx,
                'priority': priority
            }
            cleared_packages.append(cleared_info)
            print(f"  ✓ CLEARED: {pkg} (position {idx}, {priority})", file=sys.stderr)
        else:
            remaining_packages.append(pkg)

    # Report results
    cleared_count = len(cleared_packages)
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"RESULTS:", file=sys.stderr)
    print(f"  Original bounty board: {original_count} packages", file=sys.stderr)
    print(f"  Cleared (now in trusted): {cleared_count} packages", file=sys.stderr)
    print(f"  Remaining: {len(remaining_packages)} packages", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    if cleared_count > 0:
        # Log cleared packages
        append_to_cleared_log(cleared_log_path, cleared_packages)
        print(f"\n✓ Logged {cleared_count} cleared packages to {cleared_log_path}", file=sys.stderr)

        # Update bounty board
        write_bounty_board(bounty_board_path, remaining_packages)
        print(f"✓ Updated {bounty_board_path} ({len(remaining_packages)} packages)", file=sys.stderr)

        # Show cleared packages summary
        print(f"\nCleared Packages by Priority:", file=sys.stderr)
        high_priority = [p for p in cleared_packages if p['position'] <= 24]
        medium_priority = [p for p in cleared_packages if 24 < p['position'] <= 99]
        low_priority = [p for p in cleared_packages if p['position'] > 99]

        if high_priority:
            print(f"  HIGH PRIORITY ({len(high_priority)}):", file=sys.stderr)
            for p in high_priority:
                print(f"    • {p['package']}", file=sys.stderr)

        if medium_priority:
            print(f"  MEDIUM PRIORITY ({len(medium_priority)}):", file=sys.stderr)
            for p in medium_priority:
                print(f"    • {p['package']}", file=sys.stderr)

        if low_priority:
            print(f"  LOW PRIORITY ({len(low_priority)}):", file=sys.stderr)
            # Just show count for low priority to avoid spam
            print(f"    ({len(low_priority)} packages)", file=sys.stderr)

    else:
        print("\n✓ No packages were cleared. Bounty board unchanged.", file=sys.stderr)

    # Create summary statistics
    print(f"\nFinal Statistics:", file=sys.stderr)
    print(f"  Bounty Board: {len(remaining_packages)} active bounties", file=sys.stderr)
    if cleared_log_path.exists():
        total_cleared = sum(1 for line in open(cleared_log_path) if ' | ' in line)
        print(f"  Total Cleared (all time): {total_cleared} packages", file=sys.stderr)

if __name__ == '__main__':
    main()
