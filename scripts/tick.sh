#!/data/data/com.termux/files/usr/bin/bash
# tick.sh — toggle topics in TOC.md and regenerate PROGRESS.md
# Now with auto-calculated milestones.

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
  print_part "12" "Cybersecurity"
  echo
  echo "## Milestones"

  # Count per part
  p1_done=$(grep -c -e "^- \[x\] 1\." "$TOC")
  p2_done=$(grep -c -e "^- \[x\] 2\." "$TOC")

  # Helper: prints [x] if 1, [ ] if 0
  check() {
    if [ "$1" -eq 1 ]; then echo "[x]"; else echo "[ ]"; fi
  }

  # Milestone 1: any topic ticked = project pushed (assumption: once you start, you push)
  if [ "$done_count" -gt 0 ]; then
    echo "- [x] First project pushed to GitHub"
  else
    echo "- [ ] First project pushed to GitHub"
  fi

  # Milestone 2: Part 1 complete (6 topics)
  if [ "$p1_done" -eq 6 ]; then
    echo "- [x] Part 1 complete"
  else
    echo "- [ ] Part 1 complete"
  fi

  # Milestone 3: Part 2 complete (15 topics)
  if [ "$p2_done" -eq 15 ]; then
    echo "- [x] Part 2 complete"
  else
    echo "- [ ] Part 2 complete"
  fi

  # Milestone 4: 25% overall
  if [ "$percent" -ge 25 ]; then
    echo "- [x] 25% overall"
  else
    echo "- [ ] 25% overall"
  fi

  # Milestone 5: first deployed app (manual — cannot be auto-detected)
  echo "- [ ] First deployed app"

  # Milestone 6: 50% overall
  if [ "$percent" -ge 50 ]; then
    echo "- [x] 50% overall"
  else
    echo "- [ ] 50% overall"
  fi

  # Milestone 7: first capstone done (manual — requires checking Part 10)
  echo "- [ ] First capstone done"

  # Milestone 8: 100% complete
  if [ "$percent" -ge 100 ]; then
    echo "- [x] 100% complete 🎉"
  else
    echo "- [ ] 100% complete 🎉"
  fi
} > "$PROG"

echo "📊 PROGRESS.md updated ($done_count/$total — $percent%)"
