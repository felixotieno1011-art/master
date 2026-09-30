#!/data/data/com.termux/files/usr/bin/bash
# tick.sh — toggle topics in TOC.md and regenerate PROGRESS.md

MASTER="$HOME/master"
TOC="$MASTER/TOC.md"
PROG="$MASTER/PROGRESS.md"

action="$1"
topic="$2"

if [ -z "$action" ] || [ -z "$topic" ]; then
  echo "Usage: tick.sh <tick|untick|toggle> <topic>"
  exit 1
fi

line=$(grep -n -e "^- \[.\] $topic " "$TOC" | head -n1)

if [ -z "$line" ]; then
  echo "❌ Topic '$topic' not found in TOC."
  exit 1
fi

lineno=$(echo "$line" | cut -d: -f1)

case "$action" in
  tick)   sed -i "${lineno}s/\[ \]/[x]/" "$TOC" ;;
  untick) sed -i "${lineno}s/\[x\]/[ ]/" "$TOC" ;;
  toggle)
    if echo "$line" | grep -q "\[x\]"; then
      sed -i "${lineno}s/\[x\]/[ ]/" "$TOC"
    else
      sed -i "${lineno}s/\[ \]/[x]/" "$TOC"
    fi
    ;;
  *) echo "Unknown action: $action"; exit 1 ;;
esac

echo "✅ $action $topic"

# ---- Recalculate PROGRESS.md ----
total=$(grep -c -e "^- \[.\] [0-9]" "$TOC")
done_count=$(grep -c -e "^- \[x\] [0-9]" "$TOC")
remaining=$((total - done_count))
percent=0
[ "$total" -gt 0 ] && percent=$(( done_count * 100 / total ))

{
  echo "# 📊 Progress Tracker"
  echo
  echo "## Overall"
  echo "- Total topics: $total"
  echo "- Completed: $done_count"
  echo "- Remaining: $remaining"
  echo "- Progress: $percent%"
  echo "- Last updated: $(date +%Y-%m-%d\ %H:%M)"
  echo
  echo "## By Part"
  echo "| Part | Title | Done | Total | % |"
  echo "|------|-------|------|-------|---|"

  print_part() {
    local key="$1"
    local title="$2"
    local pt pd pp
    pt=$(grep -c -e "^- \[.\] ${key}\." "$TOC")
    pd=$(grep -c -e "^- \[x\] ${key}\." "$TOC")
    pp=0
    [ "$pt" -gt 0 ] && pp=$(( pd * 100 / pt ))
    echo "| $key | $title | $pd | $pt | $pp% |"
  }

  print_part "1" "Foundations"
  print_part "2" "Networking"
  print_part "3" "Programming"
  print_part "4" "Frontend"
  print_part "5" "Backend"
  print_part "6" "Databases"
  print_part "7" "DevOps"
  print_part "7.5" "Systems"
  print_part "8" "Security"
  print_part "9" "Career"
  print_part "10" "Capstone"
  print_part "11" "Specialization"

  echo
  echo "## Milestones"
  echo "- [ ] First project pushed to GitHub"
  echo "- [ ] Part 1 complete"
  echo "- [ ] Part 2 complete"
  echo "- [ ] 25% overall"
  echo "- [ ] First deployed app"
  echo "- [ ] 50% overall"
  echo "- [ ] First capstone done"
  echo "- [ ] 100% complete 🎉"
} > "$PROG"

echo "📊 PROGRESS.md updated ($done_count/$total — $percent%)"
