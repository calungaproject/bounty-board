#!/bin/bash
# Quick statistics display for bounty board status

BOUNTY_FILE="bounty-board/bounty-board.txt"
CLEARED_LOG="bounty-board/cleared-bounties.log"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           BOUNTY BOARD STATUS                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo

# Active bounties
if [ -f "$BOUNTY_FILE" ]; then
    TOTAL=$(wc -l < "$BOUNTY_FILE")
    HIGH=24
    MEDIUM=$((99 - 4))  # Adjusted for cleared packages
    LOW=$((TOTAL - HIGH - MEDIUM))

    echo "Active Bounties: $TOTAL packages"
    echo "  ├─ HIGH priority (both lists):    $HIGH packages"
    echo "  ├─ MEDIUM priority (exploit):     $MEDIUM packages"
    echo "  └─ LOW priority (lightwell):      $LOW packages"
    echo
else
    echo "⚠ Bounty file not found!"
    echo
fi

# Cleared bounties
if [ -f "$CLEARED_LOG" ]; then
    CLEARED=$(grep -c ' | ' "$CLEARED_LOG" 2>/dev/null || echo 0)
    LAST_CLEARED=$(grep ' | ' "$CLEARED_LOG" 2>/dev/null | tail -1 | cut -d'|' -f1 | xargs)

    echo "Cleared Bounties: $CLEARED packages (all time)"
    if [ -n "$LAST_CLEARED" ]; then
        echo "  └─ Last cleared: $LAST_CLEARED"
    fi
    echo
else
    echo "Cleared Bounties: 0 packages"
    echo
fi

# Top 10 current high priority
if [ -f "$BOUNTY_FILE" ]; then
    echo "Top 10 High Priority Targets:"
    head -10 "$BOUNTY_FILE" | nl -w2 -s'. '
    echo
fi

# Recent cleared
if [ -f "$CLEARED_LOG" ]; then
    RECENT=$(grep ' | ' "$CLEARED_LOG" 2>/dev/null | tail -5)
    if [ -n "$RECENT" ]; then
        echo "Recently Cleared (last 5):"
        echo "$RECENT" | while IFS='|' read -r timestamp package rest; do
            pkg_name=$(echo "$package" | xargs)
            echo "  • $pkg_name"
        done
        echo
    fi
fi

echo "──────────────────────────────────────────────────────────"
echo "Run: python3 check_cleared_bounties.py"
echo "     to check for newly cleared packages"
echo "══════════════════════════════════════════════════════════"
