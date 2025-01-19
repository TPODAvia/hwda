import requests

# Server address
server_address = "http://127.0.0.1:8000"

# Function to test different endpoints
def test_server():
    endpoints = [
        "temperature",  # Test temperature endpoint
        "pressure",     # Test pressure endpoint
        "humidity",     # Test humidity endpoint
        "weather",      # Test weather forecast endpoint
        "FF0000",       # Test turning on LED with red color
        "00FF00",       # Test turning on LED with green color
        "0000FF",       # Test turning on LED with blue color
        "FFFFFF",       # Test turning on LED with white color
        "000000",       # Test turning off LED
        "random",       # Test turning on LED with random color
    ]

    for endpoint in endpoints:
        print(f"Testing endpoint: {endpoint}")
        try:
            # Send GET request to the server
            response = requests.get(f"{server_address}/{endpoint}")
            # Print the response from the server
            print(f"Response: {response.text}\n")
        except requests.exceptions.RequestException as e:
            print(f"Error testing endpoint {endpoint}: {e}\n")

# Run the test
if __name__ == "__main__":
    test_server()
