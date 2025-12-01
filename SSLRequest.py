import requests
import ssl, socket
from datetime import datetime

from Certificate import Certificate


### Example SSL Data
# {'issuer': ((('countryName', 'IL'),),
#             (('organizationName', 'StartCom Ltd.'),),
#             (('organizationalUnitName',
#               'Secure Digital Certificate Signing'),),
#             (('commonName',
#               'StartCom Class 2 Primary Intermediate Server CA'),)),
#  'notAfter': 'Nov 22 08:15:19 2013 GMT',
#  'notBefore': 'Nov 21 03:09:52 2011 GMT',
#  'serialNumber': '95F0',
#  'subject': ((('description', '571208-SLe257oHY9fVQ07Z'),),
#              (('countryName', 'US'),),
#              (('stateOrProvinceName', 'California'),),
#              (('localityName', 'San Francisco'),),
#              (('organizationName', 'Electronic Frontier Foundation, Inc.'),),
#              (('commonName', '*.eff.org'),),
#              (('emailAddress', 'hostmaster@eff.org'),)),
#  'subjectAltName': (('DNS', '*.eff.org'), ('DNS', 'eff.org')),
#  'version': 3}


def check_ssl_info(link):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=link) as s:
            s.connect((link, 443))
            cert = s.getpeercert()

        return cert

    except requests.exceptions.SSLError:
        print("SSL Error: " + link)
        return None
    except requests.exceptions.ConnectionError:
        print("Connection Error")
        return None
    except ConnectionRefusedError:
        print("Connection Refused")
        return None
    except Exception as e:
        print(str(e))
        return None

# def print_ssl_data(issued_to, issued_by, link):
#     print(issued_to)
#     print()
#     print(issued_by)

def get_certificate_normal_time(cert_time_data):
    timestamp = ssl.cert_time_to_seconds(cert_time_data)
    date = datetime.fromtimestamp(timestamp)
    return f"{date.day}.{date.month}.{date.year}"

def parseSSLINfo(cert, link):
    subject = dict(x[0] for x in cert['subject'])
    domain = subject['commonName']

    create_time = get_certificate_normal_time(cert['notBefore'])
    end_time = get_certificate_normal_time(cert['notAfter'])

    certificate = Certificate(link,domain,create_time,end_time)
    return certificate


def get_certificate_data(domain_name):
    cert = check_ssl_info(domain_name)

    if cert is not None:
        return parseSSLINfo(cert, domain_name)
    else:
        return None


