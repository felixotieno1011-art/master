#!/bin/bash
# health-monitor.sh — Portable system health monitor
# Works on Termux/Android and normal Linux
#
# SPEC:
# 1. Detect environment (Android vs Linux)
# 2. Check CPU load + cores
# 3. Check RAM + swap
# 4. Check disk usage
# 5. Check top processes
# 6. Warn if thresholds exceeded
# 7. Print clean report

# ---- Environment detection ----
if [ -d "/data/data/com.termux" ]; then
    ENVIRONMENT="Termux (Android)"
    DISK_PATH="/data"
    LOAD_MULTIPLIER=2
    RAM_AVAILABLE_MIN=500
    SWAP_WARN_PCT=50
    DISK_WARN_PCT=85
else
    ENVIRONMENT="Linux"
    DISK_PATH="/"
    LOAD_MULTIPLIER=1
    RAM_AVAILABLE_MIN=200
    SWAP_WARN_PCT=30
    DISK_WARN_PCT=90
fi

echo "Environment: $ENVIRONMENT"
echo "Disk path:   $DISK_PATH"
echo "Thresholds:  load > $LOAD_MULTIPLIER×cores, RAM avail < ${RAM_AVAILABLE_MIN}MB, swap > ${SWAP_WARN_PCT}%, disk > ${DISK_WARN_PCT}%"

# ---- CPU section ----
CORES=$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo)

# Try /proc/loadavg first, fall back to uptime
LOAD_1MIN=$(awk '{print $1}' /proc/loadavg 2>/dev/null)
if [ -z "$LOAD_1MIN" ]; then
LOAD_1MIN=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ' ,')
fi
LOAD_THRESHOLD=$(awk -v c="$CORES" -v m="$LOAD_MULTIPLIER" 'BEGIN {print c * m}')

echo ""
echo "🔹 CPU & LOAD"
echo "   Cores:        $CORES"
echo "   Load (1 min): $LOAD_1MIN"
echo "   Threshold:    > $LOAD_THRESHOLD"

if awk -v l="$LOAD_1MIN" -v t="$LOAD_THRESHOLD" 'BEGIN {exit !(l > t)}'; then
    echo "   Status:       🔴 WARNING — system overloaded"
else
    echo "   Status:       ✅ OK"
fi

# ---- Memory section ----
TOTAL_RAM=$(free -m | awk '/^Mem:/ {print $2}')
USED_RAM=$(free -m | awk '/^Mem:/ {print $3}')
AVAILABLE_RAM=$(free -m | awk '/^Mem:/ {print $7}')
SWAP_TOTAL=$(free -m | awk '/^Swap:/ {print $2}')
SWAP_USED=$(free -m | awk '/^Swap:/ {print $3}')

if [ "$SWAP_TOTAL" -gt 0 ]; then
    SWAP_PCT=$(( SWAP_USED * 100 / SWAP_TOTAL ))
else
    SWAP_PCT=0
fi

RAM_USED_PCT=$(( USED_RAM * 100 / TOTAL_RAM ))

echo ""
echo "🔹 MEMORY"
echo "   Total RAM:     ${TOTAL_RAM} MB"
echo "   Used RAM:      ${USED_RAM} MB (${RAM_USED_PCT}%)"
echo "   Available:     ${AVAILABLE_RAM} MB"
echo "   Swap used:     ${SWAP_USED} / ${SWAP_TOTAL} MB (${SWAP_PCT}%)"

# Warning logic
MEM_WARN=0
if [ "$AVAILABLE_RAM" -lt "$RAM_AVAILABLE_MIN" ]; then
    echo "   ⚠️  Low available RAM (< ${RAM_AVAILABLE_MIN} MB)"
    MEM_WARN=1
fi
if [ "$SWAP_PCT" -gt "$SWAP_WARN_PCT" ]; then
    echo "   ⚠️  High swap usage (> ${SWAP_WARN_PCT}%)"
    MEM_WARN=1
fi
if [ "$MEM_WARN" -eq 0 ]; then
    echo "   Status:        ✅ OK"
else
    echo "   Status:        🔴 WARNING"
fi
# ---- Disk section ----
DISK_TOTAL=$(df -h "$DISK_PATH" | awk 'NR==2 {print $2}')
DISK_USED=$(df -h "$DISK_PATH" | awk 'NR==2 {print $3}')
DISK_AVAIL=$(df -h "$DISK_PATH" | awk 'NR==2 {print $4}')
DISK_PCT=$(df -h "$DISK_PATH" | awk 'NR==2 {print $5}' | tr -d '%')

echo ""
echo "🔹 STORAGE"
echo "   Partition:     $DISK_PATH"
echo "   Total:         $DISK_TOTAL"
echo "   Used:          $DISK_USED"
echo "   Available:     $DISK_AVAIL"
echo "   Usage:         ${DISK_PCT}%"

if [ "$DISK_PCT" -gt "$DISK_WARN_PCT" ]; then
    echo "   ⚠️  Disk usage above ${DISK_WARN_PCT}%"
    echo "   Status:        🔴 WARNING"
else
    echo "   Status:        ✅ OK"
fi
# ---- Top processes section ----
echo ""
echo "🔹 TOP PROCESSES (by CPU)"
echo "   (Note: on Termux you only see your own processes)"

ps aux --sort=-%cpu | grep -v -E "ps aux|awk|grep|bash health|COMMAND" | awk 'NR<=3 {printf "   %d. %-25s %s%%\n", NR, $11, $3}'
