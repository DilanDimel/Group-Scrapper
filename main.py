import requests
import json
import time

def send_to_discord(webhook_url, group_id):
    group_link = f"https://www.roblox.com/groups/{group_id}"
    data = {
        "content": f"Ownerless and unlocked group found! Group Link: {group_link}"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

    if response.status_code != 204:
        print(f"Failed to send message to Discord. Status code: {response.status_code}")

def find_ownerless_groups(webhook_url, proxy_list):
    # Replace 'START_GROUP_ID' with the group ID from where you want to start the search
    start_group_id = 10000000
    group_limit = 1000  # Number of groups to check (adjust as needed)

    proxy_index = 0  # Index to track the current proxy in the list

    for group_id in range(start_group_id, start_group_id + group_limit):
        url = f"https://groups.roblox.com/v1/groups/{group_id}"
        
        # Get the current proxy from the list and rotate to the next proxy
        current_proxy = proxy_list[proxy_index]
        proxy_protocol = current_proxy.split(':')[0].lower()
        proxy_address = current_proxy.split(':')[1]

        proxies = {
            'http': f"{proxy_protocol}://{proxy_address}",
            'https': f"{proxy_protocol}://{proxy_address}",
            'socks4': f"{proxy_protocol}://{proxy_address}",
            'socks5': f"{proxy_protocol}://{proxy_address}"
        }
        proxy_index = (proxy_index + 1) % len(proxy_list)  # Rotate to the next proxy

        response = requests.get(url, proxies=proxies)

        if response.status_code == 200:
            group_data = response.json()

            # Check if the group is ownerless and unlocked
            if group_data['owner'] is None and ('isLocked' not in group_data or not group_data['isLocked']) and group_data['publicEntryAllowed'] and group_data['publicStatus'] == 'Open':
                send_to_discord(webhook_url, group_id)

        elif response.status_code == 404:
            print(f"Group ID {group_id} does not exist.")

        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', '5'))
            print(f"Rate limited. Waiting for {retry_after} seconds before making the next request.")
            time.sleep(retry_after)

        else:
            print(f"Error fetching group ID {group_id}. Status code: {response.status_code}")

        time.sleep(1)  # Additional 1-second delay between each API request

# Replace 'WEBHOOK_URL' with the actual Discord webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1109537233196822578/vLoW7NhZHv6H_fZLRU59zS0YUdbGENACMSIIATOlJnuuUwwPy7kid3mvZL4sRoNxA6Y-'

# Read the proxy addresses from the proxy.txt file
with open('proxy.txt', 'r') as file:
    proxy_list = [line.strip() for line in file]

# Call the function to find ownerless and unlocked groups and send them to Discord
find_ownerless_groups(WEBHOOK_URL, proxy_list)
