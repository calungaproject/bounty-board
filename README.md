# Bounty Board Management

## Overview

This directory contains the prioritized bounty board for package security review work, along with tools for managing the list.

## Files

### Active Lists
- **`bounty-board.txt`** - Master bounty list (796 packages)
  - Lines 1-24: HIGH PRIORITY (in both exploit interest and lightwell lists)
  - Lines 25-99: MEDIUM PRIORITY (exploit interest only)
  - Lines 100+: LOWER PRIORITY (lightwell priority only)

### Source Lists
- **`exploit_int_packages.txt`** - Packages of interest for exploit research (99 packages)
- **`lw_prios_valid.txt`** - Lightwell priority packages, filtered (727 packages)

### Documentation
- **`summary.txt`** - Statistical breakdown of the lists
- **`ANALYSIS.md`** - Detailed analysis with recommendations

### Logs
- **`cleared-bounties.log`** - Packages that have been cleared (found in Red Hat trusted libraries)

## Usage

### Check for Cleared Bounties

Run this regularly to check if any bounty board packages have been added to Red Hat's trusted libraries:

```bash
python3 ../check_cleared_bounties.py
```

This will:
1. Fetch the current Red Hat trusted libraries index
2. Check each package in `bounty-board.txt`
3. Remove any packages now in trusted libraries
4. Log cleared packages to `cleared-bounties.log` with timestamp and priority
5. Update `bounty-board.txt` with remaining packages

### Workflow

1. **Start with high priority packages** (lines 1-24)
   - These appear in both source lists
   - Highest expected ROI

2. **Work through medium priority** (lines 25-99)
   - Exploit interest packages
   - Secondary targets

3. **Batch process lower priority** (lines 100+)
   - Volume work
   - Consider automation

4. **Regularly check for cleared packages**
   - Run `check_cleared_bounties.py` weekly
   - Cleared packages are automatically removed
   - Review `cleared-bounties.log` for progress tracking

## Statistics (Current)

- **Active Bounties:** 796 packages
- **Cleared (all time):** 5 packages
- **Last cleared:** 2026-06-26
  - langchain
  - langgraph
  - openinference-instrumentation
  - openinference-semantic-conventions

## Priority Categories

### HIGH (Lines 1-24)
Packages appearing in **both** source lists. Focus areas:
- AI/ML infrastructure (42%)
- OpenTelemetry instrumentation (17%)
- Security primitives (12%)
- Data utilities (29%)

### MEDIUM (Lines 25-99)
Exploit research interest only. Notable patterns:
- Advanced AI frameworks
- Security testing tools
- Data processing libraries

### LOW (Lines 100+)
Lightwell priority only. Suitable for:
- Automated scanning
- Batch processing
- Background work

## Maintenance

### Adding New Packages

To add packages to the bounty board:

1. Add to appropriate source list (`exploit_int_packages.txt` or `lw_prios_valid.txt`)
2. Re-run the analysis script to regenerate `bounty-board.txt`

### Removing Packages

Packages are automatically removed when found in Red Hat trusted libraries.

To manually remove a package:
1. Edit `bounty-board.txt` directly
2. Add an entry to `cleared-bounties.log` explaining the removal

## Integration

The `check_cleared_bounties.py` script can be integrated into CI/CD:

```bash
# Run weekly via cron
0 9 * * 1 cd /path/to/project && python3 check_cleared_bounties.py
```

Or as a GitHub Action for automated tracking.
