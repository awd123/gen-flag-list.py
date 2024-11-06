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

def get_detailed_country_info(wiki_url: str, json_obj: dict[str, str]):
  """Retrieve further info about a country
  
  This function takes a link to the Wikipedia page of a specific
  ISO-3166 political entity, along with a preexisting dict representing
  the political entity. The function adds further information to the
  dict."""

  # this can be slow, want to indicate progress
  print(f'Getting detailed info for {json_obj["name"]}...', file=sys.stderr)

  soup = get_soup_from_wiki(wiki_url)
  # get common name of country
  json_obj["name"] = soup.h1.span.string

  # try fetching info table for country
  info_table = soup.find("table", attrs={"class":"ib-country"})
  json_obj["sovereign"] = True

  if info_table is None:
    # dependent territories use the ib-pol-div class instead of ib-country
    json_obj["sovereign"] = False
    
    info_table = soup.find("table", attrs={"class":"ib-pol-div"})
    if info_table is None:
      # cannot scrape info
      json_obj["fullName"] = json_obj["name"]
      json_obj["capital"] = None
      json_obj["officialLanguage"] = None
      return


  table_body = info_table.tbody
  # attempt to scrape full (official) country name
  official_name = None
  try:
    official_name = table_body.find("div", attrs={"class":"country-name"}).string
  except AttributeError:
    official_name = json_obj["name"]

  json_obj["fullName"] = official_name

  capital = None
  official_language = None
  for label in table_body.find_all(attrs={"class":"infobox-label"}):
    # attempt to scrape capital
    if "Capital" in label.stripped_strings:
      capital = label.next_sibling.a.string
      continue

    # attempt to scrape official language (only supports one at the moment)
    if str(label.string) == "Official\u00a0languages": # this is a non-breaking space!
      official_language = label.next_sibling.a.string
      continue
    
  json_obj["capital"] = capital
  json_obj["officialLanguage"] = official_language

def get_all(flag_url_base: str) -> list[dict[str, str]]:
  """Get all ISO-3166 alpha-2 codes
  
  This function retrieves the ISO-3166 list of countries and
  territories from Wikipedia, then returns an array of dictionaries
  containing information about each of them.
  """

  iso3166_url = WIKIPEDIA_BASE_URL + "/wiki/ISO_3166-1_alpha-2"

  soup = get_soup_from_wiki(iso3166_url)

  countries_arr = [] # JSON array

  table_body = soup.find("table", class_="wikitable sortable sort-under").tbody # table of ISO-3166 abbreviations
  i = 0
  for row in table_body.children:
    json_obj = {}

    # attempt to get alpha-2 code
    alpha2 = row.contents[0].attrs.get('id')
    if alpha2 == None:
      continue # skip header row

    name = row.contents[1].a.string
    # get link to the country's Wikipedia page
    wiki_url = WIKIPEDIA_BASE_URL + row.contents[1].a.attrs.get('href')

    json_obj['alpha2'] = alpha2
    json_obj['name'] = name
    if (flag_url_base):
      json_obj['flagUrl'] = f"{flag_url_base}{alpha2}.png"

    get_detailed_country_info(wiki_url, json_obj)

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