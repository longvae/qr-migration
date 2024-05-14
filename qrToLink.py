import pandas as pd
import requests
import csv
import urllib.parse

# This method uses .urllib.request.urlopen to follow and redirects and return the final redirect of the URL.
def get_final_redirect(url):
    if not url.startswith("https://"):
        url = "https://" + url
    try:
        with urllib.request.urlopen(url) as response:
            final_url = response.geturl()
            return final_url
    except urllib.error.URLError as e:
        print(f"Error getting final redirect of {url}: {e}")
        return None

# This method returns any url parameters after ".com/"
def get_trailing_url_params(url):
    index = url.find(".com/")
    if index != -1:
        return url[index + len(".com/"):]
    else:
        return ""

# This method retrieves link data of a Branch link.
def get_link_data(link_id, api_key):
    encoded_link_id = urllib.parse.quote_plus(link_id)
    url = f"https://api.branch.io/v1/url?url={encoded_link_id}&branch_key={api_key}"
    headers = {
        "Content-Type": "application/json",
    }
    #print(f"\n{url}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None

# This method updates a link with a given set of link data.
def create_link(link_id, api_key, api_secret, link_data):
    url = "https://api.branch.io/v1/"
    alias = get_trailing_url_params(link_id)
    payload = {
        "branch_key": api_key,
        "branch_secret": api_secret,
    }
    payload["data"] = link_data["data"]
    if alias:
        payload["alias"] = alias

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    print("_______________________________\n")
    print(f"payload={payload}\n")

    '''response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None'''


def read_csv_and_update_links(filename):
    branch_key_live = ""  # Replace with Branch Live Key
    branch_secret = "" # Replace with Branch secret
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            x=0
            for row in reader:
                x+=1
                print(x)
                if row:  # Check if the row is not empty
                    url = row[0].strip()  # Extract URL from the first column and remove
                    #print("\nget_final_redirect call")
                    final_url = get_final_redirect(url)
                    print(f"{final_url}")
                    #if final URL is a Branch link, grab relevant link data and update base URL with that data
                    if ".app.link" in final_url:
                        link_data = get_link_data(final_url, branch_key_live)
                        create_link (url, branch_key_live, branch_secret, link_data)
                    #else update base URL with final URL as deeplink_path and canonical_url and default analytics
                    else:
                        link_data = {
                            "data" : {
                                "$deeplink_path" : final_url,
                                "$canonical_url" : final_url,
                                "~channel" : "QR",
                                "~feature" : "marketing",
                                "~campaign" : "park_QR"
                                }
                        }
                        create_link (url, branch_key_live, branch_secret, link_data)
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
filename = "qr_test.csv" # Replace with the path to .csv or QR URLs

read_csv_and_update_links(filename)

#print(get_final_redirect("https://qr.disneyworld.com/CaptCooks?r=qr"))
#link_data = get_link_data("https://thisismynew.app.link/disney_test1", "key_live_co7umEq5jRkpqhlerYDaqiebyBdnQsx1")
#create_link("https://thisismynew.app.link/disney_test1", "key_live_co7umEq5jRkpqhlerYDaqiebyBdnQsx1", "secret_live_Mgb8kfmPoPtKNkhdY3JKhXV0B95VY0Hl", link_data)
