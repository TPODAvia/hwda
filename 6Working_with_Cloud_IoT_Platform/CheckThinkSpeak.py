import requests

# ThingSpeak API URL
url = "https://api.thingspeak.com/channels/2285639/feeds.json"
api_key = "9KH02T33NWPOTZSW"

# Parameters for the request
params = {
    "api_key": api_key,
    "results": 1
}

def check_thingspeak_data():
    try:
        # Send GET request to ThingSpeak
        response = requests.get(url, params=params)

        # Print debug information for troubleshooting
        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")

        # Handle response
        if response.status_code == 200:
            data = response.json()
            feeds = data.get("feeds", [])
            if feeds:
                print("Data received successfully!")
                print("Feed Data:", feeds[0])
            else:
                print("No data available in the channel.")
        else:
            print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
            print("Response Text:", response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the check
check_thingspeak_data()
