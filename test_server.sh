#!/bin/bash

# Test if the server is running
echo "Testing connection to CSM Speech Generator server..."

curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 > /tmp/status.txt
STATUS=$(cat /tmp/status.txt)

if [ "$STATUS" == "200" ]; then
    echo "✅ SUCCESS: Server is running correctly at http://localhost:8080"
    echo "You can now open your browser and visit http://localhost:8080"
else
    echo "❌ ERROR: Server is not responding. HTTP Status: $STATUS"
    echo ""
    echo "Possible solutions:"
    echo "1. Run './run_webapp.sh' to start the server"
    echo "2. Check if port 8080 is already in use by another application"
    echo "3. Look for any error messages in the terminal when starting the server"
fi