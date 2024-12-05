@echo off
git add .
set /p commit_message="Commit mesaji: "
git commit -m "%commit_message%"
git push
pause