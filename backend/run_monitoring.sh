#!/bin/bash
# ESG System Monitoring Cron Job
# Add this to crontab with: crontab -e
# */15 * * * * /path/to/your/backend/run_monitoring.sh

cd "$(dirname "$0")"

# Run health check every 15 minutes
python3 monitor_system_health.py >> monitoring.log 2>&1

# Create backup every 6 hours (modify as needed)
HOUR=$(date +%H)
if [ $((HOUR % 6)) -eq 0 ]; then
    python3 backup_restore_system.py backup "scheduled_backup" >> monitoring.log 2>&1
    python3 backup_restore_system.py cleanup >> monitoring.log 2>&1
fi
