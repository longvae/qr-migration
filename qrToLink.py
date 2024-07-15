import pandas as pd
import requests
import csv
import urllib.parse
import argparse
import os
import pdb
from datetime import datetime
from dotenv import load_dotenv

# This global variable gets updated by the .env file or by the command line when launching this program.
ENABLE_LOGGING = False

# This method uses .urllib.request.urlopen to follow and redirects and return the final redirect of the URL.
def get_final_redirect(url):
    if not url.startswith('https://'):
        url = 'https://' + url
    #print(url)
    # try:
    #     with urllib.request.urlopen(url) as response:
    #         final_url = response.geturl()
    #         return final_url
    # except urllib.error.URLError as e:
    #     print(f"Error getting final redirect of {url}: {e}")
    #     return None
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1'
    }

    try:
        # Send a HEAD request to the endpoint, which would return redirects
        # without returning the body of the request
        response = requests.head(url, headers=headers, allow_redirects=True)
        write_to_log(f'Found {response.url} as redirect from {url}')
        return response.url
    except requests.RequestException as e:
        print('Warning: did not parse URL: {}'.format(url))
        print(e)
        write_to_log(f'WARNING: did not parse URL {url} with error: {e}')

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
    write_to_log(f'Starting request to endpoint with URL: {url}')
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        write_to_log(f'\tRetrieved link data: {response.json()} for URL {link_id}')
        return response.json()
    else:
        print("Error:", response.text)
        write_to_log(f'\tFailed to retrieve deep link data for link {link_id} with error: {response.text} and status code: {response.status_code}')
        return None

# This method updates a link with a given set of link data.
def create_link(link_id, api_key, api_secret, link_data):
    url = "https://api.branch.io/v1/url"
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
    write_to_log(f'Creating URL with payload: {payload}')

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(response.json)
        write_to_log(f'\tSuccessfully generated link with response: {response.json}')
        return response.json()
    else:
        print("Error:", response.text)
        write_to_log(f'Failed to generare a URL with error: {response.text} and status code {response.status_code}')
        return None
    
# Get the date/time string
def get_date_time_string():
    now = datetime.now()
    formatted_date_time = now.strftime('%m/%d/%Y %H:%M')
    return formatted_date_time

# Use this function to write data to a log file
def write_to_log(message):
    if not ENABLE_LOGGING:
        return
    
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the relative path to the file
    file_name = 'logging.txt'
    file_path = os.path.join(script_dir, file_name)

    with open(file_path, 'a') as output_file:
        output_file.write(message)

#this method reads the original QR urls and puts the final redirects of those urls in a csv file called temp.csv
def read_csv(filename):
    #print('Live key: ')
    #branch_key_live = input()
    #print('Secret: ')
    #branch_secret = input()
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = [row for row in reader]
            final_urls = []
            for row in rows:
                if row:  # Check if the row is not empty
                    url = row[0].strip()  # Extract URL from the first column and remove
                    final_url = get_final_redirect(url)
                    final_urls.append(final_url)
            #Update the rows with the new data in the second column
            for i, row in enumerate(rows):
                if len(row) < 2:
                    row.append(final_urls[i])
                else:
                    row[1] = final_urls[i]
        # Write the updated data back to the CSV file
        with open(filename, 'w', newline='') as file:
             writer = csv.writer(file)
             writer.writerows(rows)
        print(f"{filename} updated successfuly.")
        write_to_log(f'{filename} updated successfully')
    except Exception as e:
        print(f"An error occurred: {e}")
        write_to_log(f'An error occurred: {e}')

#this method grabs the final urls from the temp.csv file and makes a call to Branch to create the link with the corresponding link data
def update_links(filename):
    # print('Live key: ')
    # branch_key_live = input()
    branch_key_live = os.getenv('LIVE_KEY')
    # print('Secret: ')
    # branch_secret = input()
    branch_secret = os.getenv('SECRET_KEY')
    try:
        urls = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 1:
                    urls.append(row)
            print(urls)
            for url in urls:
                #if final URL is a Branch link, grab relevant link data and update base URL with that data
                if ".app.link" in url[1]:
                    link_data = get_link_data(url[1], branch_key_live)
                    create_link (url[0], branch_key_live, branch_secret, link_data)
                #else update base URL with final URL as deeplink_path and canonical_url and default analytics
                else:
                    link_data = {
                        "data" : {
                            "$deeplink_path" : url[1],
                            "$canonical_url" : url[1],
                            "~channel" : "QR",
                            "~feature" : "marketing",
                            "~campaign" : "park_QR",
                            "web_only" : "true"
                            }
                    }
                    create_link (url[0], branch_key_live, branch_secret, link_data)
#                print('\n')
#                print(link_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        write_to_log(f'Encountered an error while updating links: {e}')


def build_arg_parser():
    # Create the arg parser with argparse
    parser = argparse.ArgumentParser(description="Migrate QR codes")

    # Add arguments
    parser.add_argument('filename', type=str, help='The path and name of the file to read/udpate')
    parser.add_argument('-r', '--read', action='store_true', help='Read a file and output its contents')
    parser.add_argument('-u', '--update', action='store_true', help='Update existing QR codes')
    parser.add_argument('-l', '--logging', action='store_true', help='Enable logging')

    return parser


def str_to_bool(value):
    return value.lower() in ['true', '1', 't', 'y', 'yes']


def main():
    # Load environment variables from the .env file (e.g., keys)
    load_dotenv()

    # BE SURE TO HAVE A .env FILE IN THE ROOT DIRECTORY
    # YOUR .env file needs to have the following values:
    #   SECRET_KEY=[your Branch secret key]
    #   LIVE_KEY=[your Branch live key]
    #   ENABLE_LOGGING=false

    # Create the arg parser
    parser = build_arg_parser()

    # Parse the args
    args = parser.parse_args()

    # The filename is required as a positional argument. Read it in.
    filename = args.filename

    # Load the env_enable_logging option (this can be set independently)
    env_enable_logging = str_to_bool(os.getenv('ENABLE_LOGGING', 'false'))

    # If you specified enable logging 
    if args.logging or env_enable_logging:
        ENABLE_LOGGING = True

    # Log the program start in our log file
    write_to_log(f'\n\nSTART: {get_date_time_string()}\n')

    # You need to select an option (read vs update)
    if args.read:
        read_csv(filename)
    elif args.update:
        update_links(filename)
    else:
        print('Please select an option on the file')

    # Example usage:
    # filename = "qr_test.csv" # Replace with the path to .csv or QR URLs
    # print('Path to csv of original QR urls: ')
    # filename = input()

    # print('(a)Read or (b)Update mode?')
    # choice = input()

    # if choice == 'a' or choice == 'read':
    #     print('Read mode selected.')
    #     read_csv(filename)
    # elif choice == 'b' or choice == 'update':
    #     print ('Update mode selected.')
    #     update_links(filename)
    # else:
    #     print('Please try again.')


if __name__=='__main__':
    main()
