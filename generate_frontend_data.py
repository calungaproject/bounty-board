#!/usr/bin/env python3
"""Generate JSON data for the frontend from bounty board files."""

import json
from datetime import datetime
from pathlib import Path


def parse_bounty_board(filepath):
    """Parse bounty-board.txt into structured data."""
    bounties = []
    with open(filepath, 'r') as f:
        for idx, line in enumerate(f, 1):
            package = line.strip()
            if not package:
                continue

            # Determine priority based on line number
            if idx <= 24:
                priority = "HIGH"
                category = "Both lists (exploit + lightwell)"
            elif idx <= 99:
                priority = "MEDIUM"
                category = "Exploit interest"
            else:
                priority = "LOW"
                category = "Lightwell priority"

            bounties.append({
                "id": idx,
                "package": package,
                "priority": priority,
                "category": category
            })

    return bounties


def parse_cleared_bounties(filepath):
    """Parse cleared-bounties.log to get cleared packages."""
    cleared = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Format: YYYY-MM-DD HH:MM:SS - [PRIORITY] package_name
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    timestamp = parts[0]
                    rest = parts[1]

                    # Extract priority and package
                    if rest.startswith('['):
                        priority_end = rest.index(']')
                        priority = rest[1:priority_end]
                        package = rest[priority_end+2:].strip()
                    else:
                        priority = "UNKNOWN"
                        package = rest

                    cleared.append({
                        "timestamp": timestamp,
                        "priority": priority,
                        "package": package
                    })
    except FileNotFoundError:
        pass

    return cleared


def get_statistics(bounties, cleared):
    """Calculate statistics from the data."""
    total_active = len(bounties)
    total_cleared = len(cleared)

    priority_counts = {
        "HIGH": sum(1 for b in bounties if b["priority"] == "HIGH"),
        "MEDIUM": sum(1 for b in bounties if b["priority"] == "MEDIUM"),
        "LOW": sum(1 for b in bounties if b["priority"] == "LOW")
    }

    recent_cleared = []
    if cleared:
        sorted_cleared = sorted(cleared, key=lambda x: x["timestamp"], reverse=True)
        recent_cleared = sorted_cleared[:5]

    return {
        "total_active": total_active,
        "total_cleared": total_cleared,
        "priority_counts": priority_counts,
        "recent_cleared": recent_cleared,
        "last_updated": datetime.now().isoformat()
    }


def main():
    """Generate the frontend data JSON file."""
    base_dir = Path(__file__).parent

    bounties = parse_bounty_board(base_dir / "bounty-board.txt")
    cleared = parse_cleared_bounties(base_dir / "cleared-bounties.log")
    stats = get_statistics(bounties, cleared)

    data = {
        "bounties": bounties,
        "cleared": cleared,
        "statistics": stats
    }

    output_file = base_dir / "docs" / "data.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Generated {output_file}")
    print(f"Active bounties: {stats['total_active']}")
    print(f"Cleared bounties: {stats['total_cleared']}")
    print(f"Priority breakdown: {stats['priority_counts']}")


if __name__ == "__main__":
    main()
