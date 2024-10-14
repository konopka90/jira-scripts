#!/bin/bash

# Check if the current directory is a Git repository
if [ ! -d ".git" ]; then
  echo "This is not a Git repository!"
  exit 1
fi

# Check if the first argument is "dry-run"
dry_run=false
if [ "$1" == "dry-run" ]; then
  dry_run=true
  echo "Dry-run mode: No changes will be made, only printing the planned actions."
fi

# Fetch remote information (update branch info)
git fetch --all

# List all remote branches with the "feature/" prefix
branches=$(git branch -r | grep "origin/feature/")

# Check if any branches were found
if [ -z "$branches" ]; then
  echo "No branches found with the 'feature/' prefix"
  exit 0
fi

# Iterate over the found branches
for branch in $branches; do
  # Remove 'origin/' from the branch name
  branch_name=$(echo "$branch" | sed 's/origin\///')
  
  # Create a new branch name with the "stale/feature/" prefix
  new_branch_name="stale/$branch_name"

  if [ "$dry_run" = true ]; then
    # In dry-run mode, only print the planned actions
    echo "Would create and push a new branch '$new_branch_name' based on '$branch_name'"
  else
    # Create a local copy of the branch
    git checkout -b "$new_branch_name" "$branch_name"
    
    # Push the new branch to the remote repository
    git push origin "$new_branch_name"
    
    # Delete the local new branch
    git branch -D "$new_branch_name"
    
    # Optionally delete the old remote branch (uncomment the line below to remove old branches)
    # git push origin --delete "$branch_name"
  fi
done

# If not in dry-run mode, return to the main branch (e.g., master/main)
if [ "$dry_run" = false ]; then
  git checkout main
fi
