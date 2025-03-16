#!/bin/bash

# Reset all generated audio files
echo "Cleaning up generated audio files..."
rm -rf /Users/dina/code/csm-mlx/static/audio/*.wav

# Make sure the directory still exists
mkdir -p /Users/dina/code/csm-mlx/static/audio

echo "Done! All previously generated audio files have been removed."
echo "The web interface will continue to work and will generate new files."