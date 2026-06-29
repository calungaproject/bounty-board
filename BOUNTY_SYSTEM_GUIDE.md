# Bounty Board System Guide

## Overview

A complete system for managing security bounty package priorities, with automatic tracking of packages that have been cleared (added to Red Hat's trusted libraries).

## Quick Start

```bash
# View current status
./bounty_stats.sh

# Check for cleared packages (run weekly)
python3 check_cleared_bounties.py

# View detailed analysis
cat ANALYSIS.md
```

## System Components

### 1. Active Bounty Board

**`bounty-board.txt`** - Priority-sorted master list

Structure:
```
Lines   1-24  : HIGH PRIORITY
Lines  25-99  : MEDIUM PRIORITY
Lines 100-796 : LOW PRIORITY
```

Current: **796 active packages**

### 2. Cleared Bounties Tracking

**`check_cleared_bounties.py`** - Automatic clearing script
- Fetches Red Hat trusted libraries index
- Compares against active bounties
- Removes cleared packages
- Logs with timestamp, position, priority

**`cleared-bounties.log`** - Historical record
- All cleared packages with timestamps
- Original position and priority level
- Useful for progress tracking

### 3. Monitoring Tools

**`bounty_stats.sh`** - Quick status display
```bash
./bounty_stats.sh
# Shows:
# - Active bounty counts by priority
# - Total cleared packages
# - Top 10 current targets
# - Recently cleared packages
```

## Workflow

### Daily/Weekly Operations

1. **Start work session**
   ```bash
   ./bounty_stats.sh  # Check current status
   ```

2. **Work through priorities**
   - Focus on lines 1-24 (HIGH priority)
   - Expected highest ROI

3. **Weekly clearing check**
   ```bash
   python3 check_cleared_bounties.py
   # Automatically:
   # - Checks for newly trusted packages
   # - Updates bounty board
   # - Logs cleared packages
   ```

### Priority Guidance

#### HIGH Priority (24 packages, lines 1-24)
**Work on these first** - Maximum impact

Categories:
- **AI/ML Ecosystem** (10 packages)
  - arize-phoenix, huggingface-hub, litellm, tokenizers, spacy, thinc, pyarrow, etc.
  - High attack surface, critical infrastructure

- **OpenTelemetry Instrumentation** (4 packages)
  - openinference-instrumentation-* packages
  - Observability layers, potential side channels

- **Security & Auth** (3 packages)
  - pkce, requests-futures, gitpython
  - Authentication primitives, supply chain

- **Data & Utilities** (7 packages)
  - Templating, data structures, URL handling

#### MEDIUM Priority (71 packages, lines 25-99)
Secondary focus targets

Characteristics:
- Advanced frameworks
- Security testing tools
- Specialized libraries

#### LOW Priority (701 packages, lines 100-796)
Volume work - consider automation

Suitable for:
- Batch processing
- Automated scanning
- Background work

## Scripts Reference

### `check_cleared_bounties.py` ⭐
**Run this regularly** - Main maintenance script

```bash
python3 check_cleared_bounties.py
# Checks: All bounty packages vs. trusted libraries
# Updates: bounty-board.txt (removes cleared)
# Logs: cleared-bounties.log (with details)
```

Features:
- Fetches latest Red Hat index
- Smart package name normalization
- Priority-aware logging
- Atomic file updates
- Detailed statistics

### `bounty_stats.sh`
Quick status dashboard

```bash
./bounty_stats.sh
# Shows snapshot of current state
```

### `generate_frontend_data.py`
Generates static HTML dashboard

```bash
python3 generate_frontend_data.py
# Outputs: docs/index.html (complete static site)
```

## File Structure

```
.
├── bounty-board.txt                (MASTER LIST - 796 packages)
├── cleared-bounties.log            (cleared packages history)
├── ANALYSIS.md                     (detailed analysis)
├── README.md                       (directory guide)
├── check_cleared_bounties.py       (maintenance: clear)
├── bounty_stats.sh                 (monitoring: status)
├── generate_frontend_data.py       (frontend: generate HTML)
├── docs/
│   └── index.html                  (public dashboard)
├── .github/
│   └── workflows/
│       ├── update-bounties.yml     (auto-check cleared)
│       └── deploy-pages.yml        (auto-deploy dashboard)
└── BOUNTY_SYSTEM_GUIDE.md          (this file)
```

## Statistics (Current)

| Metric | Count |
|--------|-------|
| Active bounties | 796 |
| HIGH priority | 24 |
| MEDIUM priority | 71 |
| LOW priority | 701 |
| Cleared (all time) | 5 |
| Last cleared | 2026-06-26 |

## GitHub Integration

### Automated Workflows

The repository includes two GitHub Actions workflows:

1. **Update Bounty Board** - Weekly automated check
   - Runs `check_cleared_bounties.py`
   - Commits changes automatically
   - Uploads logs as artifacts

2. **Deploy Dashboard** - Automatic deployment
   - Generates static HTML
   - Deploys to GitHub Pages
   - Updates on every push to main

### Setup

1. Enable GitHub Actions in repository settings
2. Enable GitHub Pages (Source: "GitHub Actions")
3. Configure workflow permissions: "Read and write"

## Automation Options

### Cron Job (Weekly Check)
```bash
# Add to crontab
0 9 * * 1 cd /path/to/project && python3 check_cleared_bounties.py >> cron.log 2>&1
```

### Git Hook (Pre-commit)
```bash
#!/bin/bash
# .git/hooks/pre-commit
python3 check_cleared_bounties.py --quiet
```

## Best Practices

1. **Check weekly** - Run `check_cleared_bounties.py` every Monday
2. **Review logs** - Check `cleared-bounties.log` for progress
3. **Focus on HIGH** - Lines 1-24 are highest ROI
4. **Track progress** - Use `bounty_stats.sh` for quick status
5. **Document findings** - Add notes to cleared log if manual removal

## Troubleshooting

### Script fails to fetch trusted libraries
```bash
# Test connectivity
curl -I https://packages.redhat.com/trusted-libraries/python

# Check with verbose output
python3 check_cleared_bounties.py 2>&1 | less
```

### Package not clearing despite being trusted
- Check package name normalization (underscore vs. hyphen)
- Verify exact spelling in trusted libraries index
- Manual review may be needed

### Want to manually clear a package
```bash
# 1. Edit bounty-board.txt (remove line)
# 2. Add to cleared-bounties.log
echo "$(date '+%Y-%m-%d %H:%M:%S') | package-name | Manual removal | Reason" >> cleared-bounties.log
```

## Maintenance

### Updating Package List

To add new packages:

1. Edit `bounty-board.txt` directly, placing packages in appropriate priority section
2. Run `python3 generate_frontend_data.py` to update dashboard
3. Run `python3 check_cleared_bounties.py` to check against trusted libraries

### Archive Old Logs

Periodically archive cleared-bounties.log:
```bash
cp cleared-bounties.log cleared-bounties-$(date +%Y%m%d).log
```

## Support

For issues or questions about the bounty system:
1. Check this guide
2. Review `README.md`
3. Check `ANALYSIS.md` for package insights
4. Review script comments for technical details
