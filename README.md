# Bounty Board Management

## Overview

This directory contains the prioritized bounty board for package security review work, along with tools for managing the list.

## Files

### Active Lists
- **`bounty-board.txt`** - Master bounty list (1,721 packages)
  - Lines 1-24: HIGH PRIORITY (from multiple priority sources)
  - Lines 25-99: MEDIUM PRIORITY (secondary priority)
  - Lines 100+: LOWER PRIORITY (remaining packages)

### Source Datasets
- **`datasets/`** - Directory containing source package lists
  - `dataset_00.txt` - 727 packages
  - `dataset_01.txt` - 99 packages
  - `dataset_02.txt` - 1,000 packages
  - Merged automatically via `update_bounty_board.py`

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
   - Highest expected ROI

2. **Work through medium priority** (lines 25-99)
   - Secondary targets

3. **Batch process lower priority** (lines 100+)
   - Volume work
   - Consider automation

4. **Regularly check for cleared packages**
   - Run `check_cleared_bounties.py` weekly
   - Cleared packages are automatically removed
   - Review `cleared-bounties.log` for progress tracking

## Statistics (Current)

- **Active Bounties:** 1,721 packages
- **Cleared (all time):** 8 packages
- **Last cleared:** 2026-06-29
  - matplotlib-inline
  - appdirs
  - ipython
  - PyPika
  - langchain (and 3 others)

## Priority Categories

### HIGH (Lines 1-24)
Highest priority packages. Focus areas:
- AI/ML infrastructure (42%)
- OpenTelemetry instrumentation (17%)
- Security primitives (12%)
- Data utilities (29%)

### MEDIUM (Lines 25-99)
Medium priority packages. Notable patterns:
- Advanced AI frameworks
- Security testing tools
- Data processing libraries

### LOW (Lines 100+)
Lower priority packages. Suitable for:
- Automated scanning
- Batch processing
- Background work

## Maintenance

### Adding New Packages

#### Option 1: Add via Dataset Files (Recommended)

1. Add packages to a new or existing file in `datasets/` directory
   - Name format: `dataset_XX.txt` (e.g., `dataset_03.txt`)
   - One package per line
2. Run the update script:
   ```bash
   python3 update_bounty_board.py
   ```
   - Automatically merges all datasets into `bounty-board.txt`
   - Removes duplicates
   - Preserves priority structure
3. Regenerate frontend:
   ```bash
   python3 generate_frontend_data.py
   ```

#### Option 2: Manual Edit

1. Edit `bounty-board.txt` directly, placing packages in the appropriate priority section
2. Re-run `generate_frontend_data.py` to update the dashboard

### Removing Packages

Packages are automatically removed when found in Red Hat trusted libraries.

To manually remove a package:
1. Edit `bounty-board.txt` directly
2. Add an entry to `cleared-bounties.log` explaining the removal

## GitHub Integration

### Automated Updates

The repository includes two GitHub Actions workflows:

#### 1. Update Bounty Board (`.github/workflows/update-bounties.yml`)

Automatically checks for cleared bounties and updates the board:
- **Schedule**: Weekly on Monday at 9 AM UTC
- **Triggers**: Manual dispatch, or changes to relevant files
- **Actions**:
  - Runs `check_cleared_bounties.py`
  - Commits any changes to `bounty-board.txt` and `cleared-bounties.log`
  - Uploads cleared bounties log as artifact

#### 2. Deploy GitHub Pages (`.github/workflows/deploy-pages.yml`)

Builds and deploys the frontend dashboard:
- **Trigger**: Push to main branch, or manual dispatch
- **Actions**:
  - Generates fully static HTML from current bounty data
  - Deploys to GitHub Pages (works without JavaScript)

### Setup Instructions

1. **Enable GitHub Actions**:
   - Ensure Actions are enabled in repository settings

2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: "GitHub Actions"
   - The site will be available at `https://<username>.github.io/<repo-name>/`

3. **Configure Permissions**:
   - Settings → Actions → General → Workflow permissions
   - Enable "Read and write permissions"

### Frontend Dashboard

The live dashboard displays:
- Current bounty statistics (pre-rendered)
- Complete bounty list (all 1,721 packages)
- Recently cleared packages
- Priority breakdown
- Last update timestamp

**Features:**
- Fully static HTML - works without JavaScript
- Progressive enhancement: search and filtering require JavaScript
- Fast loading - all content pre-rendered server-side

Access the dashboard at your GitHub Pages URL once deployed.

## Local Development

### Generate Static HTML Site

```bash
python3 generate_frontend_data.py
```

This generates `docs/index.html` with all bounty data pre-rendered.

### Preview Site Locally

```bash
cd docs
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

The site is fully functional without JavaScript - all content is visible. JavaScript provides optional filtering and search enhancements.
