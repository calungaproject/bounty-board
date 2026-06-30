#!/usr/bin/env python3
"""
Fetch GitHub PRs from calungaproject/index with "pkg onboarding" label.
Outputs to calunga-index-prs.json
"""

import json
import os
import sys
import urllib.request
import urllib.error


def fetch_github_prs(owner, repo, label):
    """
    Fetch PRs from GitHub API with specified label.
    Handles pagination to get all PRs.

    Args:
        owner: Repository owner
        repo: Repository name
        label: Label to filter by

    Returns:
        List of PR data dictionaries
    """
    base_url = "https://api.github.com"
    endpoint = f"/repos/{owner}/{repo}/pulls"

    # Check for GitHub token (optional but recommended for rate limits)
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    all_prs = []
    page = 1
    per_page = 100

    while True:
        params = f"?state=all&per_page={per_page}&page={page}"
        url = f"{base_url}{endpoint}{params}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                page_prs = json.loads(response.read().decode())

            if not page_prs:
                break

            all_prs.extend(page_prs)
            print(f"Fetched page {page} ({len(page_prs)} PRs)")

            # If we got fewer than per_page, we've reached the end
            if len(page_prs) < per_page:
                break

            page += 1

        except urllib.error.HTTPError as e:
            print(f"Error fetching PRs: {e.code} {e.reason}", file=sys.stderr)
            if e.code == 401:
                print("Authentication failed. Set GITHUB_TOKEN environment variable.", file=sys.stderr)
            elif e.code == 403:
                print("Rate limit exceeded. Set GITHUB_TOKEN for higher limits.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Filter PRs by label
    filtered_prs = []
    for pr in all_prs:
        pr_labels = [l['name'] for l in pr.get('labels', [])]
        if label in pr_labels:
            filtered_prs.append(pr)

    return filtered_prs


def extract_package_name(pr):
    """
    Extract package name from PR title.
    Titles follow pattern: "Onboard <package-name>"
    """
    title = pr.get('title', '')

    # Pattern: "Onboard package-name"
    if title.lower().startswith('onboard '):
        return title[8:].strip()

    # Fallback patterns for edge cases
    title_lower = title.lower()

    if 'onboard' in title_lower:
        parts = title.split()
        for i, part in enumerate(parts):
            if part.lower() == 'onboard' and i + 1 < len(parts):
                return parts[i + 1].strip()

    # Last resort: return the whole title
    return title.strip()


def format_pr_data(prs):
    """
    Format PR data into required structure.

    Returns:
        Dictionary with package names as keys and lists of PRs as values
    """
    result = {}

    for pr in prs:
        package_name = extract_package_name(pr)

        pr_data = {
            'link': pr['html_url'],
            'status': pr['state'],  # 'open' or 'closed'
            'number': pr['number'],
            'title': pr['title'],
            'created_at': pr['created_at'],
            'updated_at': pr['updated_at']
        }

        # Add merged status if available
        if pr['state'] == 'closed' and pr.get('merged_at'):
            pr_data['merged'] = True
            pr_data['merged_at'] = pr['merged_at']
        else:
            pr_data['merged'] = False

        # Group PRs by package name
        if package_name not in result:
            result[package_name] = []
        result[package_name].append(pr_data)

    return result


def main():
    owner = "calungaproject"
    repo = "index"
    label = "pkg onboarding"
    output_file = "calunga-index-prs.json"

    print(f"Fetching PRs from {owner}/{repo} with label '{label}'...")

    prs = fetch_github_prs(owner, repo, label)
    print(f"Found {len(prs)} PRs with label '{label}'")

    formatted_data = format_pr_data(prs)

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(formatted_data, f, indent=2)

    # Calculate summary statistics
    total_prs = sum(len(pr_list) for pr_list in formatted_data.values())
    all_prs = [pr for pr_list in formatted_data.values() for pr in pr_list]
    open_count = sum(1 for pr in all_prs if pr['status'] == 'open')
    closed_count = sum(1 for pr in all_prs if pr['status'] == 'closed')
    merged_count = sum(1 for pr in all_prs if pr.get('merged'))

    print(f"Written {len(formatted_data)} packages with {total_prs} total PRs to {output_file}")

    print(f"\nSummary:")
    print(f"  Unique packages: {len(formatted_data)}")
    print(f"  Total PRs: {total_prs}")
    print(f"  Open: {open_count}")
    print(f"  Closed: {closed_count}")
    print(f"  Merged: {merged_count}")


if __name__ == "__main__":
    main()
