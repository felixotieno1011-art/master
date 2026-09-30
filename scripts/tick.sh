#!/data/data/com.termux/files/usr/bin/bash
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

total=$(grep -c -e "^- \[.\] [0-9]" "$TOC")
done_count=$(grep -c -e "^- \[x\] [0-9]" "$TOC")
remaining=$((total - done_count))
percent=0
[ "$total" -gt 0 ] && percent=$(( done_count * 100 / total ))

parts=("Foundations" "Networking" "Programming" "Frontend" "Backend" "Databases" "DevOps" "Security" "Career" "Capstone" "Specialization")

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
  for i in $(seq 1 11); do
    part_total=$(grep -c -e "^- \[.\] $i\." "$TOC")
    part_done=$(grep -c -e "^- \[x\] $i\." "$TOC")
    part_pct=0
    [ "$part_total" -gt 0 ] && part_pct=$(( part_done * 100 / part_total ))
    title="${parts[$((i-1))]}"
    echo "| $i | $title | $part_done | $part_total | $part_pct% |"
  done
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
