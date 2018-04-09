""" Censys subdomain finder """
#!/usr/bin/env python3

# superfluous-parens
# pylint: disable=C0325

import os
import sys
import time
import subprocess
import censys.certificates
import censys.ipv4
import censys
import cli


def find_subdomains(domain, api_id, api_secret):
    """ Finds subdomains of a domain using Censys API """
    try:
        censys_certificates = censys.certificates.CensysCertificates(
            api_id=api_id, api_secret=api_secret)
        certificate_query = 'parsed.names: %s' % domain
        certificates_search_results = censys_certificates.search(
            certificate_query, fields=['parsed.names'])

        # Flatten the result, and remove duplicates
        subdomains = []
        for search_result in certificates_search_results:
            subdomains.extend(search_result['parsed.names'])

        return set(subdomains)
    except censys.base.CensysUnauthorizedException:
        sys.stderr.write('[-] Your Censys credentials look invalid.\n')
        exit(1)
    except censys.base.CensysRateLimitExceededException:
        sys.stderr.write('[-] Looks like you exceeded your Censys account limits rate. Exiting\n')
        exit(1)


def filter_subdomains(domain, subdomains):
    """  Filters out uninteresting subdomains """
    return [subdomain for subdomain in subdomains
            if '*' not in subdomain and subdomain.endswith(domain)]


def print_subdomains(domain, subdomains, time_ellapsed):
    """ Prints the list of found subdomains to stdout """
    if len(subdomains) is 0:
        print('[-] Did not find any subdomain')
        return

    print('[*] Found %d unique subdomain%s of %s in ~%s seconds\n' %
          (len(subdomains), 's' if len(subdomains) > 1 else '', domain,
           str(time_ellapsed)))
    for subdomain in subdomains:
        print('  - ' + subdomain)
    print('')


def save_subdomains_to_file(subdomains, output_file):
    """ Saves the list of found subdomains to an output file """
    if output_file is None or len(subdomains) is 0:
        return

    try:
        with open(output_file, 'w') as f:
            for subdomain in subdomains:
                f.write(subdomain + '\n')

        print('[*] Wrote %d subdomains to %s\n' % (len(subdomains), os.path.abspath(output_file)))
    except IOError as e:
        sys.stderr.write('[-] Unable to write to output file %s : %s\n' % (output_file, e))


def main(domain=None, output_file=None, censys_api_id=None,
         censys_api_secret=None, resolve=False):
    """ Main init """
    print('[*] Searching Censys for subdomains of %s' % domain)
    start_time = time.time()
    subdomains = find_subdomains(domain, censys_api_id, censys_api_secret)
    subdomains = filter_subdomains(domain, subdomains)
    end_time = time.time()
    time_ellapsed = round(end_time - start_time, 1)
    print_subdomains(domain, subdomains, time_ellapsed)
    save_subdomains_to_file(subdomains, output_file)

    if resolve == True:
        print('[+] Resolving found domains\n')
        with open(output_file, 'r') as f:
            target_domains = f.readlines()

        results = [domain.strip() for domain in target_domains]
        output_file += '.dns'
        for tdomain in results:
            try:
                res = subprocess.check_output("/usr/bin/host "  + tdomain, shell=True)
                with open(output_file, 'a') as f:
                    f.write(str(res).rstrip() + '\n')
            except subprocess.CalledProcessError as e:
                with open(output_file, 'a') as f:
                    f.write(str(e).rstrip() + '\n')
                continue
        print('\n[*] Wrote dns2ip to %s\n' % os.path.abspath(output_file))

if __name__ == "__main__":
    ARGS = cli.PARSER.parse_args()

   #CENSYS_API_ID = None
   #CENSYS_API_SECRET = None

    if 'CENSYS_API_ID' in os.environ and 'CENSYS_API_SECRET' in os.environ:
        CENSYS_API_ID = os.environ['CENSYS_API_ID']
        CENSYS_API_SECRET = os.environ['CENSYS_API_SECRET']

    if ARGS.CENSYS_API_ID and ARGS.CENSYS_API_SECRET:
        CENSYS_API_ID = ARGS.CENSYS_API_ID
        CENSYS_API_SECRET = ARGS.CENSYS_API_SECRET

    if None in [CENSYS_API_ID, CENSYS_API_SECRET]:
        sys.stderr.write('''[!] Please set your Censys API ID and secret from
            your environment (CENSYS_API_ID and CENSYS_API_SECRET) or from the
            command line.\n''')
        exit(1)

    main(ARGS.domain, ARGS.output_file, CENSYS_API_ID, CENSYS_API_SECRET,
         ARGS.RESOLVE)
