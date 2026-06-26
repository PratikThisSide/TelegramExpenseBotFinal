#!/bin/bash
# Use /data for persistent storage (Render persistent disk)
export DB_PATH="${DB_PATH:-/data/expenses.db}"
mkdir -p /data
python bot.py
