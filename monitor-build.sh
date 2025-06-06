#!/bin/bash
# Build monitoring wrapper script

# Configuration
CHECK_INTERVAL=30  # seconds between checks
MAX_ATTEMPTS=120   # maximum number of checks

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
PROCESS_NAME=""
BUILD_COMMAND=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--process)
            PROCESS_NAME="$2"
            shift 2
            ;;
        -c|--command)
            BUILD_COMMAND="$2"
            shift 2
            ;;
        -i|--interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        -m|--max-attempts)
            MAX_ATTEMPTS="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$PROCESS_NAME" ] || [ -z "$BUILD_COMMAND" ]; then
    echo "Usage: $0 -p|--process PROCESS_NAME -c|--command \"BUILD_COMMAND\" [options]"
    echo "Options:"
    echo "  -i, --interval SECONDS    Seconds between checks (default: $CHECK_INTERVAL)"
    echo "  -m, --max-attempts NUM    Maximum number of checks (default: $MAX_ATTEMPTS)"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Generate log filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$SCRIPT_DIR/logs/build_${TIMESTAMP}.log"

# Run the monitor script with the provided parameters
python3 "$SCRIPT_DIR/scripts/monitor_build.py" \
    "$PROCESS_NAME" \
    "$BUILD_COMMAND" \
    --interval "$CHECK_INTERVAL" \
    --attempts "$MAX_ATTEMPTS" 2>&1 | tee "$LOG_FILE"

# Check the exit status
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "📝 Log saved to: $LOG_FILE"
else
    echo "❌ Build monitoring failed or build did not complete successfully"
    echo "📝 Check the log file for details: $LOG_FILE"
    exit 1
fi
