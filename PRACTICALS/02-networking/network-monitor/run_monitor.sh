#!/data/data/com.termux/files/usr/bin/bash
# Runs monitor.py N times with pauses.
# Usage: bash run_monitor.sh [runs] [pause_seconds]

RUNS=${1:-10}
PAUSE=${2:-5}

trap 'echo ""; echo "🛑 Stopped by user."; exit 0' INT

echo "🚀 Running monitor $RUNS time(s), pause ${PAUSE}s"
echo ""

for i in $(seq 1 "$RUNS"); do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Run $i of $RUNS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python monitor.py

    if [ "$i" -lt "$RUNS" ]; then
        echo "⏳ Waiting ${PAUSE}s..."
        sleep "$PAUSE"
    fi
done

echo ""
echo "✅ All $RUNS runs complete."
echo "   Report: python report.py --html"
