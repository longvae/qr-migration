# QR Code Migration

This script assists with migrating QR codes from a 3rd-party provider to Branch links. It's intended to be used by Branchsters who are assisting a customer who wants their pre-existing QR codes to function as Branch links.

## Getting Started

The script has to be run in two steps. Step 1 is loading the redirects/link data behind the existing links. This has to be done first because once the CNAME change happens, we can't retrieve the original redirects and need to have them archived. Step 2 is creating the new Branch links; this needs to happen immediately after the domain used for pre-existing QR codes is CNAME'd to Branch. This effectively recreates all of the existing links in Branch so that we can handle requests (clicks) from them.

1. Update the `.env` file to include a `LIVE_KEY' and a `SECRET_KEY` for your Branch app.
2. Load a CSV file with URLs that need conversion.
3. Run the "read" part of the program.
4. Request customer makes CNAME change.
5. Immediately after the CNAME change is made (and validated), run the "update" part of the program to recreate those links in Branch.

## Caveats

- True "web-only" support isn't possible for pre-created links. This is because we cannot change the actual domain that users click on; typically, web-only involves adding an exclusion path (iOS) or a different subdomiain (Android, which doesn't support exclusion paths). Since we cannot change the pre-existing QR code URLs, this is not possible. Instead "web-only" support in this case refers to having the app open (if it's installed), then kick out to web. It's up to the customer as to whether they want to open the browser (Safari/Chrome/etc.) or launch an in-app browser for web-only links. The script will simply check to see if the final URL is not a Branch link and append web-only as metadata to the newly created Branch link.
