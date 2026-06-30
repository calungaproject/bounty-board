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
from datetime import datetime, timezone


def fetch_github_prs(owner, repo, label, since_date="2026-05-01"):
    """
    Fetch PRs from GitHub API with specified label using search API.
    Handles pagination to get all PRs.

    Args:
        owner: Repository owner
        repo: Repository name
        label: Label to filter by
        since_date: ISO date string (YYYY-MM-DD) to filter PRs created on or after this date

    Returns:
        List of PR data dictionaries
    """
    base_url = "https://api.github.com"
    endpoint = "/search/issues"

    # Check for GitHub token (optional but recommended for rate limits)
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    # Build search query: is:pr repo:owner/repo label:"label" created:>=YYYY-MM-DD
    from urllib.parse import quote
    query = f'is:pr repo:{owner}/{repo} label:"{label}" created:>={since_date}'

    all_prs = []
    page = 1
    per_page = 100

    while True:
        params = f"?q={quote(query)}&per_page={per_page}&page={page}&sort=created&order=desc"
        url = f"{base_url}{endpoint}{params}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            items = data.get('items', [])
            if not items:
                break

            all_prs.extend(items)
            print(f"Fetched page {page} ({len(items)} PRs)")

            # If we got fewer than per_page, we've reached the end
            if len(items) < per_page:
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

    return all_prs


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


def fetch_check_status(owner, repo, pr_number, sha, token=None):
    """
    Fetch check run status for a PR's latest commit.

    Returns:
        Dictionary with check status information
    """
    if not sha:
        return None

    base_url = "https://api.github.com"
    endpoint = f"/repos/{owner}/{repo}/commits/{sha}/check-runs"
    url = f"{base_url}{endpoint}"

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        check_runs = data.get('check_runs', [])

        if not check_runs:
            return None

        # Aggregate check status and track failed checks
        statuses = {
            'success': 0,
            'failure': 0,
            'pending': 0,
            'skipped': 0,
            'total': len(check_runs)
        }

        failed_checks = []
        pending_checks = []

        for check in check_runs:
            conclusion = check.get('conclusion')
            status = check.get('status')
            name = check.get('name', 'Unknown')

            if conclusion == 'success':
                statuses['success'] += 1
            elif conclusion in ['failure', 'timed_out', 'action_required']:
                statuses['failure'] += 1
                failed_checks.append({
                    'name': name,
                    'conclusion': conclusion,
                    'url': check.get('html_url')
                })
            elif conclusion == 'skipped':
                statuses['skipped'] += 1
            elif status == 'in_progress' or status == 'queued':
                statuses['pending'] += 1
                pending_checks.append(name)

        # Determine overall status
        if statuses['failure'] > 0:
            overall = 'failure'
        elif statuses['pending'] > 0:
            overall = 'pending'
        elif statuses['success'] > 0:
            overall = 'success'
        else:
            overall = 'unknown'

        result = {
            'overall': overall,
            'details': statuses
        }

        # Add failed check details if any
        if failed_checks:
            result['failed_checks'] = failed_checks

        # Add pending check names if any
        if pending_checks:
            result['pending_checks'] = pending_checks

        return result

    except Exception as e:
        # Don't fail the whole script if check fetching fails
        return None


def format_pr_data(prs, owner, repo, token=None, fetch_checks=True):
    """
    Format PR data into required structure.

    Returns:
        Dictionary with package names as keys and lists of PRs as values
    """
    result = {}
    total = len(prs)

    for idx, pr in enumerate(prs, 1):
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

        # Fetch check status for open PRs
        if fetch_checks and pr['state'] == 'open':
            sha = pr.get('head', {}).get('sha')
            if sha:
                if idx % 10 == 0:
                    print(f"Fetching checks for PR #{pr['number']} ({idx}/{total})...", end='\r')
                check_status = fetch_check_status(owner, repo, pr['number'], sha, token)
                if check_status:
                    pr_data['checks'] = check_status

        # Group PRs by package name
        if package_name not in result:
            result[package_name] = []
        result[package_name].append(pr_data)

    if fetch_checks:
        print()  # Clear the progress line

    return result


def main():
    owner = "calungaproject"
    repo = "index"
    label = "pkg onboarding"
    output_file = "calunga-index-prs.json"

    # Get GitHub token
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')

    print(f"Fetching PRs from {owner}/{repo} with label '{label}' since 2026-05-01...")

    prs = fetch_github_prs(owner, repo, label, since_date="2026-05-01")
    print(f"Found {len(prs)} PRs with label '{label}' created since 2026-05-01")

    print(f"\nFormatting PR data and fetching check status...")
    formatted_data = format_pr_data(prs, owner, repo, token, fetch_checks=True)

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(formatted_data, f, indent=2)

    # Calculate summary statistics
    total_prs = sum(len(pr_list) for pr_list in formatted_data.values())
    all_prs = [pr for pr_list in formatted_data.values() for pr in pr_list]
    open_count = sum(1 for pr in all_prs if pr['status'] == 'open')
    closed_count = sum(1 for pr in all_prs if pr['status'] == 'closed')
    merged_count = sum(1 for pr in all_prs if pr.get('merged'))

    # Check statistics
    prs_with_checks = sum(1 for pr in all_prs if 'checks' in pr)
    failed_checks = sum(1 for pr in all_prs if pr.get('checks', {}).get('overall') == 'failure')
    pending_checks = sum(1 for pr in all_prs if pr.get('checks', {}).get('overall') == 'pending')
    passing_checks = sum(1 for pr in all_prs if pr.get('checks', {}).get('overall') == 'success')

    print(f"Written {len(formatted_data)} packages with {total_prs} total PRs to {output_file}")

    print(f"\nSummary:")
    print(f"  Unique packages: {len(formatted_data)}")
    print(f"  Total PRs: {total_prs}")
    print(f"  Open: {open_count}")
    print(f"  Closed: {closed_count}")
    print(f"  Merged: {merged_count}")

    if prs_with_checks > 0:
        print(f"\nCheck Status:")
        print(f"  PRs with checks: {prs_with_checks}")
        print(f"  Passing: {passing_checks}")
        print(f"  Failing: {failed_checks}")
        print(f"  Pending: {pending_checks}")


if __name__ == "__main__":
    main()
