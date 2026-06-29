#!/usr/bin/env python3
"""Generate static HTML site from bounty board files."""

from datetime import datetime
from pathlib import Path
import html


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
                category = "High priority - multiple sources"
            elif idx <= 99:
                priority = "MEDIUM"
                category = "Medium priority"
            else:
                priority = "LOW"
                category = "Lower priority"

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

                # Format: YYYY-MM-DD HH:MM:SS | package-name | Position: N | Priority: LEVEL
                parts = line.split(' | ')
                if len(parts) >= 2:
                    timestamp = parts[0].strip()
                    package = parts[1].strip()

                    # Extract priority if available
                    priority = "UNKNOWN"
                    if len(parts) >= 4:
                        priority_part = parts[3].strip()
                        if priority_part.startswith('Priority:'):
                            priority = priority_part.replace('Priority:', '').strip()

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

    return {
        "total_active": total_active,
        "total_cleared": total_cleared,
        "priority_counts": priority_counts,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    }


def generate_bounty_html(bounties):
    """Generate HTML for bounty items."""
    html_parts = []
    for bounty in bounties:
        package = html.escape(bounty["package"])
        category = html.escape(bounty["category"])
        priority = bounty["priority"]

        html_parts.append(f'''
            <div class="bounty-item" data-priority="{priority}" data-package="{package.lower()}">
                <div class="bounty-info">
                    <div class="package-name">{package}</div>
                    <div class="package-category">{category}</div>
                </div>
                <div class="priority-badge priority-{priority}">{priority}</div>
            </div>
        ''')

    return '\n'.join(html_parts)


def generate_cleared_html(cleared):
    """Generate HTML for cleared bounties."""
    if not cleared:
        return ''

    # Get 5 most recent
    recent = sorted(cleared, key=lambda x: x["timestamp"], reverse=True)[:5]

    html_parts = []
    for item in recent:
        package = html.escape(item["package"])
        timestamp = html.escape(item["timestamp"])

        html_parts.append(f'''
            <div class="cleared-item">
                <span class="cleared-package">{package}</span>
                <span class="cleared-date">{timestamp}</span>
            </div>
        ''')

    section_html = f'''
        <div class="cleared-section">
            <h2>Recently Cleared Bounties</h2>
            <div class="cleared-list">
                {''.join(html_parts)}
            </div>
        </div>
    '''

    return section_html


def generate_html(bounties, cleared, stats):
    """Generate complete HTML page."""

    bounties_html = generate_bounty_html(bounties)
    cleared_html = generate_cleared_html(cleared)

    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bounty Board - Package Security Review</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .controls {{
            padding: 30px 40px;
            background: white;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .search-box {{
            flex: 1;
            min-width: 250px;
        }}

        .search-box input {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #e9ecef;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.3s;
        }}

        .filter-btn:hover {{
            border-color: #667eea;
            color: #667eea;
        }}

        .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .bounty-list {{
            padding: 40px;
        }}

        .bounty-item {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .bounty-item.hidden {{
            display: none;
        }}

        .bounty-item:hover {{
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }}

        .bounty-info {{
            flex: 1;
        }}

        .package-name {{
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            font-family: 'Monaco', 'Courier New', monospace;
        }}

        .package-category {{
            font-size: 0.85em;
            color: #6c757d;
            margin-top: 5px;
        }}

        .priority-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .priority-HIGH {{
            background: #dc3545;
            color: white;
        }}

        .priority-MEDIUM {{
            background: #ffc107;
            color: #333;
        }}

        .priority-LOW {{
            background: #28a745;
            color: white;
        }}

        .cleared-section {{
            padding: 40px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}

        .cleared-section h2 {{
            margin-bottom: 20px;
            color: #333;
        }}

        .cleared-item {{
            background: white;
            border-left: 4px solid #28a745;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .cleared-package {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-weight: 600;
        }}

        .cleared-date {{
            color: #6c757d;
            font-size: 0.9em;
        }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
            font-size: 1.1em;
            display: none;
        }}

        .no-results.visible {{
            display: block;
        }}

        footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}

            .filter-buttons {{
                width: 100%;
                justify-content: center;
            }}

            .bounty-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Bounty Board</h1>
            <p>Package Security Review Priorities</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{stats['total_active']}</div>
                <div class="label">Active Bounties</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['priority_counts']['HIGH']}</div>
                <div class="label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['priority_counts']['MEDIUM']}</div>
                <div class="label">Medium Priority</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['total_cleared']}</div>
                <div class="label">Cleared</div>
            </div>
        </div>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="search" placeholder="Search packages...">
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="ALL">All</button>
                <button class="filter-btn" data-filter="HIGH">High</button>
                <button class="filter-btn" data-filter="MEDIUM">Medium</button>
                <button class="filter-btn" data-filter="LOW">Low</button>
            </div>
        </div>

        <div class="bounty-list">
            {bounties_html}
            <div class="no-results">No bounties found matching your criteria.</div>
        </div>

        {cleared_html}

        <footer>
            <p>Last updated: {stats['last_updated']}</p>
            <p>Automated updates via GitHub Actions</p>
        </footer>
    </div>

    <noscript>
        <style>
            .controls {{ display: none; }}
        </style>
    </noscript>

    <script>
        // Progressive enhancement - filtering and search with JavaScript
        let currentFilter = 'ALL';
        let searchTerm = '';

        function filterBounties() {{
            const items = document.querySelectorAll('.bounty-item');
            const noResults = document.querySelector('.no-results');
            let visibleCount = 0;

            items.forEach(item => {{
                const priority = item.dataset.priority;
                const packageName = item.dataset.package;

                const matchesFilter = currentFilter === 'ALL' || priority === currentFilter;
                const matchesSearch = searchTerm === '' || packageName.includes(searchTerm.toLowerCase());

                if (matchesFilter && matchesSearch) {{
                    item.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    item.classList.add('hidden');
                }}
            }});

            if (visibleCount === 0) {{
                noResults.classList.add('visible');
            }} else {{
                noResults.classList.remove('visible');
            }}
        }}

        document.getElementById('search').addEventListener('input', (e) => {{
            searchTerm = e.target.value;
            filterBounties();
        }});

        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                currentFilter = e.target.dataset.filter;
                filterBounties();
            }});
        }});
    </script>
</body>
</html>'''

    return template


def main():
    """Generate the static HTML site."""
    base_dir = Path(__file__).parent

    bounties = parse_bounty_board(base_dir / "bounty-board.txt")
    cleared = parse_cleared_bounties(base_dir / "cleared-bounties.log")
    stats = get_statistics(bounties, cleared)

    html_content = generate_html(bounties, cleared, stats)

    output_file = base_dir / "docs" / "index.html"
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"Generated {output_file}")
    print(f"Active bounties: {stats['total_active']}")
    print(f"Cleared bounties: {stats['total_cleared']}")
    print(f"Priority breakdown: {stats['priority_counts']}")


if __name__ == "__main__":
    main()
