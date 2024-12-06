# https://hosting-checker.net/websites/amazon.com

import requests

def MaiServer(url):
    requesturl = f"https://hosting-checker.net/api/hosting/{url}"
    response = requests.get(requesturl)
    mailserverdata = response.json()

    incomingmailserver = []
    outgoingmailserver = []

    if len(mailserverdata["incomingMail"]["providers"]) != 0:
        for i in mailserverdata["incomingMail"]["providers"]:
            mailserver = {
                "organization": i["organization"],
                "domain": i["domain"],
                "country": i["country"],
                "asn": i["asNumber"],
                "path": ' → '.join(i["paths"][0])
            }
            incomingmailserver.append(mailserver)

    if len(mailserverdata["outgoingMail"]["providers"]) != 0:    
        for i in mailserverdata["outgoingMail"]["providers"]:
            mailserver = {
                "organization": i["organization"],
                "domain": i["domain"],
                "country": i["country"],
                "asn": i["asNumber"],
                "path": ' → '.join(i["paths"][0])
            }
            outgoingmailserver.append(mailserver)
    
    return incomingmailserver, outgoingmailserver

# print(MaiServer("amazon.com"))