#!/bin/bash

# Directory Queue System
# Usage: ./queue.sh <command>
# Commands: init, push <file>, pop, peek, count, list, clear, process <command>

QUEUE_DIR="$HOME/.dirqueue"
QUEUE_IN="$QUEUE_DIR/in"
QUEUE_PROCESSING="$QUEUE_DIR/processing"
QUEUE_DONE="$QUEUE_DIR/done"
QUEUE_FAILED="$QUEUE_DIR/failed"

# Initialize queue directories
init_queue() {
    mkdir -p "$QUEUE_IN" "$QUEUE_PROCESSING" "$QUEUE_DONE" "$QUEUE_FAILED"
    echo "Queue initialized in $QUEUE_DIR"
}

# Push a file to queue
push_to_queue() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "Error: File '$file' not found"
        return 1
    fi
    
    local filename=$(basename "$file")
    local timestamp=$(date +%Y%m%d_%H%M%S)
    cp "$file" "$QUEUE_IN/${timestamp}_${filename}"
    echo "Pushed: $filename"
}

# Pop next item from queue
pop_from_queue() {
    local next_file=$(ls -tr "$QUEUE_IN" 2>/dev/null | head -n 1)
    if [ -z "$next_file" ]; then
        echo "Queue is empty"
        return 1
    fi
    
    mv "$QUEUE_IN/$next_file" "$QUEUE_PROCESSING/"
    echo "$next_file"
}

# Peek at next item
peek_queue() {
    local next_file=$(ls -tr "$QUEUE_IN" 2>/dev/null | head -n 1)
    if [ -z "$next_file" ]; then
        echo "Queue is empty"
        return 1
    fi
    echo "$next_file"
}

# Count items in queue
count_queue() {
    local count=$(ls -1 "$QUEUE_IN" 2>/dev/null | wc -l)
    echo "Items in queue: $count"
    echo "Items processing: $(ls -1 "$QUEUE_PROCESSING" 2>/dev/null | wc -l)"
    echo "Items completed: $(ls -1 "$QUEUE_DONE" 2>/dev/null | wc -l)"
    echo "Items failed: $(ls -1 "$QUEUE_FAILED" 2>/dev/null | wc -l)"
}

# List all items in queue
list_queue() {
    echo "In Queue:"
    ls -lh "$QUEUE_IN" 2>/dev/null
    echo -e "\nProcessing:"
    ls -lh "$QUEUE_PROCESSING" 2>/dev/null
    echo -e "\nCompleted:"
    ls -lh "$QUEUE_DONE" 2>/dev/null
    echo -e "\nFailed:"
    ls -lh "$QUEUE_FAILED" 2>/dev/null
}

# Clear all queues
clear_queue() {
    read -p "Are you sure you want to clear all queues? [y/N] " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        rm -rf "$QUEUE_IN"/* "$QUEUE_PROCESSING"/* "$QUEUE_DONE"/* "$QUEUE_FAILED"/*
        echo "All queues cleared"
    fi
}

# Process queue with given command
process_queue() {
    local command="$1"
    if [ -z "$command" ]; then
        echo "Error: Command required"
        return 1
    }
    
    while true; do
        local file=$(pop_from_queue)
        if [ $? -ne 0 ]; then
            break
        fi
        
        echo "Processing: $file"
        local full_path="$QUEUE_PROCESSING/$file"
        
        if eval "$command \"$full_path\""; then
            mv "$full_path" "$QUEUE_DONE/"
            echo "Success: $file"
        else
            mv "$full_path" "$QUEUE_FAILED/"
            echo "Failed: $file"
        fi
    done
}

# Main command handler
case "$1" in
    "init")
        init_queue
        ;;
    "push")
        if [ -z "$2" ]; then
            echo "Usage: $0 push <file>"
            exit 1
        fi
        push_to_queue "$2"
        ;;
    "pop")
        pop_from_queue
        ;;
    "peek")
        peek_queue
        ;;
    "count")
        count_queue
        ;;
    "list")
        list_queue
        ;;
    "clear")
        clear_queue
        ;;
    "process")
        if [ -z "$2" ]; then
            echo "Usage: $0 process <command>"
            exit 1
        fi
        process_queue "$2"
        ;;
    *)
        echo "Usage: $0 <command>"
        echo "Commands: init, push <file>, pop, peek, count, list, clear, process <command>"
        exit 1
        ;;
esac
