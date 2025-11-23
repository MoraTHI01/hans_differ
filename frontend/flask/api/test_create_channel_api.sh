#!/bin/bash

echo "Getting JWT token..."

# Get JWT token using basic auth
python3 -c "
import requests
import base64
import json

# Create basic auth header
credentials = 'pikachu25@th-nuernberg.de:l4=rD3SQ5tMe0U'
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Make login request to the Flask API
response = requests.get('http://localhost:5001/api/login',
                       headers={'Authorization': f'Basic {encoded_credentials}'})

print('TOKEN_RESPONSE_START')
print(response.text)
print('TOKEN_RESPONSE_END')
"

echo "Extracting access token..."

# Extract access token from response
TOKEN_RESPONSE=$(python3 -c "
import requests
import base64
import json

# Create basic auth header
credentials = 'pikachu25@th-nuernberg.de:l4=rD3SQ5tMe0U'
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Make login request to the Flask API
response = requests.get('http://localhost:5001/api/login',
                       headers={'Authorization': f'Basic {encoded_credentials}'})

print(response.text)
")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Failed to get access token"
    echo "Response was: $TOKEN_RESPONSE"
    exit 1
fi

echo "Got access token: ${ACCESS_TOKEN:0:20}..."

echo "Testing createChannel API call..."

# Make API call to create channel
python3 -c "
import requests
import json

access_token = '$ACCESS_TOKEN'

# Channel data
channel_data = {
    'language': 'en',
    'course': 'dummy',
    'course_acronym': 'dm',
    'semester': 'Dummy Semester 2024',
    'lecturer': 'Dummy Lecturer',
    'faculty': 'Dummy Faculty',
    'faculty_acronym': 'DF',
    'faculty_color': '#2F9B92',
    'university': 'Technische Hochschule Ingolstadt',
    'university_acronym': 'THI',
    'license': 'OER',
    'license_url': 'https://open-educational-resources.de',
    'tags': 'dm',
    'thumbnails_lecturer': 'http://localhost/avatars/avatar-m-00001.png',
    'archive_channel_content': True
}

# Make API call to the Flask API
response = requests.post('http://localhost:5001/api/createChannel',
                        headers={'Content-Type': 'application/json',
                                'Authorization': f'Bearer {access_token}'},
                        json=channel_data)

print(f'Status Code: {response.status_code}')
print(f'Response: {response.text}')
"

echo ""
echo "API call completed"
