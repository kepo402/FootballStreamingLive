import requests

# Replace with your actual credentials and URLs
login_url = 'https://authentication.dstv.com/registration/signin'
redirect_uri = 'https://www.dstv.com/en-ng/watch/stream-with-dstv'
login_data = {
    'email': 'alawodeolayinka2@gmail.com',  # Replace with your actual email
    'password': '27855869',            # Replace with your actual password
    'redirect_uri': redirect_uri,
    'client_id': '158beb80-7a28-4d67-9f64-f6808e20da29',
    'usejwt': 'true',
    'lang': 'en-ng',
    'prompt': 'login'
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Send the POST request to login
response = requests.post(login_url, data=login_data, headers=headers, allow_redirects=False)

# Print the response status and headers for debugging
print("Status Code:", response.status_code)
print("Response Headers:", response.headers)
print("Response Text:", response.text)

# Check if login was successful
if response.status_code == 302:
    # Extract the token from the Location header
    location_header = response.headers.get('Location')
    if location_header:
        # Parse the token from the URL
        params = dict(param.split('=') for param in location_header.split('?')[1].split('&'))
        access_token = params.get('access_token')
        print("Access Token:", access_token)
    else:
        print("No Location header found.")
else:
    print("Login failed with status code:", response.status_code)
