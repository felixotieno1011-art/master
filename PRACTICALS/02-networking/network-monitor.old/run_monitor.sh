#!/data/data/com.termux/files/usr/bin/bash
# ============================================
# run_monitor.sh — Runs monitor.py N times with pauses
# ============================================

RUNS=10
PAUSE=5   # seconds between runs

# Handle Ctrl+C gracefully
trap 'echo ""; echo "🛑 Stopped by user. Total completed runs above."; exit 0' INT

echo "🚀 Running network monitor $RUNS times (pause: ${PAUSE}s)"
echo "   Press Ctrl+C to stop anytime."
echo ""

for i in $(seq 1 $RUNS); do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Run $i of $RUNS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python monitor.py

    if [ $i -lt $RUNS ]; then
        echo ""
        echo "⏳ Waiting ${PAUSE}s before next run..."
        sleep $PAUSE
    fi
done

echo ""
echo "✅ All $RUNS runs complete. Check network_log.txt"
