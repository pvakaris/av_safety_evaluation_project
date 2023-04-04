#!/bin/bash
find . -name __pycache__ -type d -exec rm -rf {} +

find . -name ".*" -type f -delete

find . -name "*.sh" -exec chmod +x {} \;