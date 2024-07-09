import pandas as pd
import requests
import csv
import urllib.parse
import argparse
import pdb

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
        response = requests.head(url, headers=headers, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        print('Warning: did not parse URL: {}'.format(url))
        print(e)

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

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(response.json)
        return response.json()
    else:
        print("Error:", response.text)
        return None

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
    except Exception as e:
        print(f"An error occurred: {e}")

#this method grabs the final urls from the temp.csv file and makes a call to Branch to create the link with the corresponding link data
def update_links(filename):
    print('Live key: ')
    branch_key_live = input()
    print('Secret: ')
    branch_secret = input()
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


def build_arg_parser():
    # Create the arg parser with argparse
    parser = argparse.ArgumentParser(description="Migrate QR codes")

    # Add arguments
    parser.add_argument('filename', type=str, help='The path and name of the file to read/udpate')
    parser.add_argument('-r', '--read', action='store_true', help='Read a file and output its contents')
    parser.add_argument('-u', '--update', action='store_true', help='Update existing QR codes')

    return parser


def main():
    # Create the arg parser
    parser = build_arg_parser()

    # Parse the args
    parser.parse_args()

    # The filename is required as a positional argument. Read it in.
    filename = parser.filename

    # You need to select an option (read vs update)
    if parser.read:
        read_csv(filename)
    elif parser.update:
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
