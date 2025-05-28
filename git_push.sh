#!/bin/bash

# 1. Stage all files
git add .

# 2. Unstage the commit_msg file (if it was staged)
git reset commit_msg

# 3. Remove all __pycache__ directories from staging (without deleting actual files)
find . -type d -name "__pycache__" -exec git rm -r --cached {} +

# 4. Append the content of commit_msg to commit_msgs
cat commit_msg >> commit_msgs

# 5. Commit using the content of commit_msg as the commit message
git commit -F commit_msg

# 6. Get the current branch name dynamically
current_branch=$(git symbolic-ref --short HEAD)

# 7. Push to the current branch (to avoid branch name mismatch issues)
git push origin "$current_branch"
