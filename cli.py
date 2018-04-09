""" Command line configs and options """
import argparse

PARSER = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

PARSER.add_argument(
    'domain',
    help='The domain to scan'
)

PARSER.add_argument(
    '-o', '--output',
    help='A file to output the list of subdomains to',
    dest='output_file'
)

PARSER.add_argument(
    '-r', '--resolve',
    help='Resolve domains to IPs using host command - not stealth',
    dest='RESOLVE',
    action='store_true'
)

PARSER.add_argument(
    '--censys-api-id',
    help='Censys API ID. Can also be defined using the CENSYS_API_ID environment variable',
    dest='CENSYS_API_ID'
)

PARSER.add_argument(
    '--censys-api-secret',
    help='Censys API secret. Can also be defined using the CENSYS_API_SECRET environment variable',
    dest='CENSYS_API_SECRET'
)
