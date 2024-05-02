# MKV Track Remover

MKV Track Remover is a Python tool designed to automate the removal of specified audio and subtitle tracks from MKV files.

## Features

- Removes unwanted audio and subtitle tracks from MKV files.
- Allows configuration of which tracks to keep based on language, default status, and other settings.

## Prerequisites

Before running the MKV Track Remover, ensure you have completed the following steps:

### Steps
1. **Install MKVToolNix**: Download and install it from [here](https://mkvtoolnix.download/).
2. **Install pymkv**: Install this Python library which serves as an interface to MKVToolNix.
   ```
   pip install git+https://github.com/sheldonkwoodward/pymkv.git@release/1.0.9 
   ```
4. Add MKVToolNix to the system's PATH: Ensure that MKVToolNix is accessible from the command line by adding it to your system's PATH.
5. Update the config file to match your use case.

## Caution
This tool has not been thoroughly tested. Use it at your own risk.
