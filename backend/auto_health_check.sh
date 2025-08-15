#!/bin/bash
# Auto Health Check - Ensures ESG system is always working
# Run this script regularly (e.g., via cron job) to prevent issues

echo "🚀 ESG System Auto Health Check Started"
echo "Time: $(date)"
echo "======================================"

# Step 1: Check if Django server is running
echo "📡 Checking Django server..."
if curl -s http://localhost:3001/api/auth/csrf/ > /dev/null; then
    echo "✅ Django server is running"
else
    echo "❌ Django server not responding"
    echo "🔧 Attempting to start Django server..."
    
    # Try to start Django in background (adjust path as needed)
    cd /mnt/c/Users/20100/v3/backend
    nohup python3 manage.py runserver 0.0.0.0:3001 > server.log 2>&1 &
    
    echo "⏳ Waiting for server to start..."
    sleep 10
    
    if curl -s http://localhost:3001/api/auth/csrf/ > /dev/null; then
        echo "✅ Django server started successfully"
    else
        echo "❌ Failed to start Django server"
        exit 1
    fi
fi

# Step 2: Run comprehensive health check
echo ""
echo "🏥 Running comprehensive health check..."
python3 monitor_system_health.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo "✅ System health check passed"
    echo "📧 No action required"
else
    echo "❌ System health check failed"
    echo "📧 Alert: ESG system needs attention"
    
    # In production, you would send alerts here:
    # - Email notifications
    # - Slack messages  
    # - SMS alerts
    # - etc.
fi

echo ""
echo "🏁 Health check completed at $(date)"
echo "======================================"