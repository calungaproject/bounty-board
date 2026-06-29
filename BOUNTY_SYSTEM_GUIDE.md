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
cat bounty-board/ANALYSIS.md
```

## System Components

### 1. Source Data
- **`lightwell/lightwell_prios_sanitized.csv`** - Original Lightwell priorities (1,216 packages)
- **`bounty-board/exploit_int_packages.txt`** - Exploit research interests (99 packages)

### 2. Filtering Pipeline
```
lightwell_prios_sanitized.csv (1,216)
         ↓
   filter_packages.py
         ↓ (removes trusted + failed PRs)
lw_prios_valid.txt (727)
         ↓
   analyze_bounty_board.py
         ↓ (merges with exploit_int)
bounty-board.txt (800 → 796)
```

### 3. Active Bounty Board

**`bounty-board/bounty-board.txt`** - Priority-sorted master list

Structure:
```
Lines   1-24  : HIGH PRIORITY (in both lists)
Lines  25-99  : MEDIUM PRIORITY (exploit interest only)
Lines 100-796 : LOW PRIORITY (lightwell only)
```

Current: **796 active packages**

### 4. Cleared Bounties Tracking

**`check_cleared_bounties.py`** - Automatic clearing script
- Fetches Red Hat trusted libraries index
- Compares against active bounties
- Removes cleared packages
- Logs with timestamp, position, priority

**`bounty-board/cleared-bounties.log`** - Historical record
- All cleared packages with timestamps
- Original position and priority level
- Useful for progress tracking

### 5. Monitoring Tools

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
   - These are in BOTH exploit interest and lightwell lists
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
Exploit research targets - secondary focus

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

### `filter_packages.py`
Filters Lightwell CSV against:
- Red Hat trusted libraries
- Failed GitHub onboarding PRs

```bash
python3 filter_packages.py
# Output: lightwell/lw_prios_valid.txt
```

### `analyze_bounty_board.py`
Merges and analyzes two package lists

```bash
python3 analyze_bounty_board.py
# Outputs:
# - bounty-board/bounty-board.txt (master list)
# - bounty-board/summary.txt (stats)
```

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

## File Structure

```
├── lightwell/
│   ├── lightwell_prios_sanitized.csv   (original data)
│   └── lw_prios_valid.txt              (filtered)
├── bounty-board/
│   ├── bounty-board.txt                (MASTER LIST - 796 packages)
│   ├── exploit_int_packages.txt        (source: exploit interest)
│   ├── lw_prios_valid.txt              (source: lightwell valid)
│   ├── cleared-bounties.log            (cleared packages history)
│   ├── summary.txt                     (statistics)
│   ├── ANALYSIS.md                     (detailed analysis)
│   └── README.md                       (directory guide)
├── filter_packages.py                  (step 1: filter)
├── analyze_bounty_board.py             (step 2: merge)
├── check_cleared_bounties.py           (maintenance: clear)
├── bounty_stats.sh                     (monitoring: status)
└── BOUNTY_SYSTEM_GUIDE.md              (this file)
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

## Recent Activity

**Cleared on 2026-06-26 14:41:05:**
- langchain (MEDIUM priority, position 46)
- langgraph (MEDIUM priority, position 51)
- openinference-instrumentation (MEDIUM, position 69)
- openinference-semantic-conventions (MEDIUM, position 80)

## Automation Options

### Cron Job (Weekly Check)
```bash
# Add to crontab
0 9 * * 1 cd /path/to/project && python3 check_cleared_bounties.py >> bounty-board/cron.log 2>&1
```

### Git Hook (Pre-commit)
```bash
#!/bin/bash
# .git/hooks/pre-commit
python3 check_cleared_bounties.py --quiet
```

### CI/CD Integration
```yaml
# GitHub Actions example
name: Check Cleared Bounties
on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly Monday 9am
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check cleared bounties
        run: python3 check_cleared_bounties.py
      - name: Commit changes
        run: |
          git config user.name "Bounty Bot"
          git add bounty-board/
          git commit -m "Update cleared bounties" || true
          git push
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
echo "$(date '+%Y-%m-%d %H:%M:%S') | package-name | Manual removal | Reason" >> bounty-board/cleared-bounties.log
```

## Maintenance

### Updating Source Lists

When new packages are added to sources:

1. Update `exploit_int_packages.txt` or rerun filter on new Lightwell CSV
2. Regenerate bounty board:
   ```bash
   python3 analyze_bounty_board.py
   ```
3. Run clearing check:
   ```bash
   python3 check_cleared_bounties.py
   ```

### Archive Old Logs

Periodically archive cleared-bounties.log:
```bash
cp bounty-board/cleared-bounties.log bounty-board/cleared-bounties-$(date +%Y%m%d).log
# Keep recent entries only if needed
```

## Support

For issues or questions about the bounty system:
1. Check this guide
2. Review `bounty-board/README.md`
3. Check `bounty-board/ANALYSIS.md` for package insights
4. Review script comments for technical details
