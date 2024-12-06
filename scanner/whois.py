import requests

def GetWhois(url):
    requesturl = "https://who-dat.as93.net/" + url
    response = requests.get(requesturl)
    whoisdata = response.json()

    domaindetails = {
        "url": whoisdata["domain"]["domain"],
        "domainname": whoisdata["domain"]["name"],
        "domainextension": whoisdata["domain"]["extension"],
        "domainid": whoisdata["domain"]["id"],
        "status": whoisdata["domain"]["status"],
        "domaincreated": whoisdata["domain"]["created_date_in_time"],
        "domainupdated": whoisdata["domain"]["updated_date_in_time"],
        "domainexpiration": whoisdata["domain"]["expiration_date_in_time"]
    }

    registrar = {
        "registrarid": whoisdata["registrar"]["id"],
        "registrarname": whoisdata["registrar"]["name"],
        "registrarphone": whoisdata["registrar"]["phone"],
        "registraremail": whoisdata["registrar"]["email"],
        "registrarsite": whoisdata["registrar"]["referral_url"]
    }

    registrant = {
        'registrantname': whoisdata["registrant"]["name"],
        'registrantorganization': whoisdata["registrant"]["organization"],
        'registrantstreet': whoisdata["registrant"]["street"], 
        'registrantcity': whoisdata["registrant"]["city"],
        'registrantprovince': whoisdata["registrant"]["province"],
        'registrantpostalcode': whoisdata["registrant"]["postal_code"],
        'registrantcountry': whoisdata["registrant"]["country"],
        'registrantphone': whoisdata["registrant"]["phone"],
        'registrantemail': whoisdata["registrant"]["email"]
    }

    administrative = {
        'administrativename': whoisdata["administrative"]["name"],
        'administrativeorganization': whoisdata["administrative"]["organization"],
        'administrativestreet': whoisdata["administrative"]["street"], 
        'administrativecity': whoisdata["administrative"]["city"],
        'administrativeprovince': whoisdata["administrative"]["province"],
        'administrativepostalcode': whoisdata["administrative"]["postal_code"],
        'administrativecountry': whoisdata["administrative"]["country"],
        'administrativephone': whoisdata["administrative"]["phone"],
        'administrativeemail': whoisdata["administrative"]["email"]
    }

    technical = {
        'technicalname': whoisdata["technical"]["name"],
        'technicalorganization': whoisdata["technical"]["organization"],
        'technicalstreet': whoisdata["technical"]["street"], 
        'technicalcity': whoisdata["technical"]["city"],
        'technicalprovince': whoisdata["technical"]["province"],
        'technicalpostalcode': whoisdata["technical"]["postal_code"],
        'technicalcountry': whoisdata["technical"]["country"],
        'technicalphone': whoisdata["technical"]["phone"],
        'technicalemail': whoisdata["technical"]["email"]
    }

    return domaindetails, registrar, registrant, administrative, technical

# print(domaindetails)
# print()
# print(registrar)
# print()
# print(registrant)
# print()
# print(administrative)
# print()
# print(technical)

# print(GetWhois("techmedok.com"))