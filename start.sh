#!/bin/bash
set -e
echo "Starting backend on port ${PORT:-7860}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}
