import requests

# Define the ThingSpeak URL
THINGSPEAK_URL = "https://api.thingspeak.com/channels/2813583/feeds.json?api_key=9KH02T33NWPOTZSW&results=2"

def check_thingspeak():
    try:
        # Send a GET request to ThingSpeak
        response = requests.get(THINGSPEAK_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response as JSON
        data = response.json()
        
        # Check if there are any messages
        feeds = data.get("feeds", [])
        if feeds:
            print("Message found:")
            for feed in feeds:
                print(feed)
        else:
            print("No messages found.")
    except requests.exceptions.RequestException as e:
        print(f"Error checking ThingSpeak: {e}")

# Call the function
check_thingspeak()