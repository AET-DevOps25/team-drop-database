#!/bin/bash

# Base directory
base_dir="$(pwd)/server"

# Subfolders under 'server'
subfolders=("attractionService" "userService" "authService")

# Iterate through each subfolder and run docker compose
for dir in "${subfolders[@]}"; do
  full_path="$base_dir/$dir"
  echo "Navigating to $full_path"
  if [ -d "$full_path" ]; then
    cd "$full_path"
    echo "Running docker compose up in $(pwd)"
    docker compose up -d
  else
    echo "Directory $full_path does not exist."
  fi
done

# Return to original directory
cd "$base_dir/.."
