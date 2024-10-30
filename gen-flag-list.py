"""Generate flag list

This script generates a JSON file from the Wikipedia article for the ISO-3166
standard. As of right now, the generated file includes each country's
name and alpha-2 code, and optionally a URL pointing to the country's flag.
The base URL for the generated flag urls must be specified on the command
line. E.g.:
  python3 gen-flag-list.py list.json https://example.com/flags/
The generated JSON will then look like:
...
  {
    "alpha2": "AE",
    "name": "United Arab Emirates",
    "flagUrl": "https://example.com/flags/AE.png"
  }
...
The base URL must end in a trailing slash.
"""

import json
import sys
import requests
from bs4 import BeautifulSoup

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"

def get_soup_from_wiki(wiki_url: str) -> BeautifulSoup:
  """Get BeautifulSoup object from Wikipedia page"""

  response = requests.get(wiki_url)
  # strip newlines (or else they will show up in the soup)
  stripped_content = ''.join(response.text.splitlines())
  soup = BeautifulSoup(stripped_content, 'html.parser') # create soup

  return soup

def get_all(flag_url_base: str) -> list[dict[str, str]]:
  """Get all ISO-3166 alpha-2 codes
  
  This function retrieves the ISO-3166 list of countries and
  territories from Wikipedia, then returns an array of dictionaries
  containing information about each of them.
  """

  iso3166_url = WIKIPEDIA_BASE_URL + "/wiki/ISO_3166-1_alpha-2"

  soup = get_soup_from_wiki(iso3166_url)

  countries_arr = [] # JSON array

  table_body = soup.find("table", class_="wikitable sortable sort-under").contents[0] # table of ISO-3166 abbreviations
  i = 0
  for row in table_body.children:
    json_obj = {}
    # attempt to get alpha-2 code
    alpha2 = row.contents[0].attrs.get('id')
    if alpha2 == None:
      continue # skip header row
    name = row.contents[1].a.string
    json_obj['alpha2'] = alpha2
    json_obj['name'] = name
    if (flag_url_base):
      json_obj['flagUrl'] = f"{flag_url_base}{alpha2}.png"

    countries_arr.append(json_obj)

  return countries_arr

# process command-line args and run script
if len(sys.argv) < 2:
  print("Error: must specify name of output file", file=sys.stderr)
  sys.exit(1)

# allows specifying a base for flag URLs as the second command-line argument
flag_url_base = None
if len(sys.argv) == 3:
  flag_url_base = sys.argv[2]

countries_arr = get_all(flag_url_base)
with open(sys.argv[1], 'w', encoding='utf-8') as outf:
  json.dump(countries_arr, outf, indent=2)

print("Success", file=sys.stderr)