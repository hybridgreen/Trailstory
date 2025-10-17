# test-upload.sh
#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0cmFpbHN0b3J5Iiwic3ViIjoiZTZkNTkyY2UtNzA1Mi00MDhhLThmMzctYTFjMDRiYzBjOTZlIiwiaWF0IjoxNzYwNjcxMjExLCJleHAiOjE3NjA2NzQ4MTF9.LaLaSWf12MmJ-NuqKd3eFNbKAvg-q0tYvQkAZQFiFtQ"
TRIP_ID="5170829f-8b97-43cb-8544-b544fcfcb49f"

curl -X POST http://localhost:8000/trips/$TRIP_ID/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/yasseryaya-oye/workspace/hybridgreen/Trailstory/samples/Takao-18KM.gpx" \
  -F "trip_id=15432536" \
  -F "title=Day 1" \
  -F "notes=Great ride" \
  -F "date=2025-01-12"