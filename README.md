# gen-flag-list.py

This script generates a JSON file from
[the Wikipedia article for the ISO-3166 alpha-2 standard](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).
As of right now, the generated file includes each country's
name and alpha-2 code, and optionally a URL pointing to the country's flag.
The base URL for the generated flag URLs must be specified on the command
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