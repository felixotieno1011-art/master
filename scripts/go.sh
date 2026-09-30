#!/data/data/com.termux/files/usr/bin/bash
case "$1" in
  note)  shift; f=$(ls "$HOME/master/NOTES/" | grep "^0$1" | head -n1); nano "$HOME/master/NOTES/$f" ;;
  work)  shift; d=$(ls "$HOME/master/PRACTICALS/" | grep "^0$1" | head -n1); cd "$HOME/master/PRACTICALS/$d" && exec bash ;;
  toc)   nano "$HOME/master/TOC.md" ;;
  log)   nano "$HOME/master/JOURNAL.md" ;;
  res)   nano "$HOME/master/RESOURCES.md" ;;
  prog)  nano "$HOME/master/PROGRESS.md" ;;
  *)     cd "$HOME/master" && exec bash ;;
esac
