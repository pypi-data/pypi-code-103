import boto3
import time

from pprint import pprint
from bullet import Bullet, Input, styles, VerticalPrompt, Check, YesNo

r53domains = boto3.client('route53domains')

def get_user_picked_domains_to_change():
    # List Route 53 domains
    response = r53domains.list_domains()
    domain_list = []
    for domain in response["Domains"]:
        domain_list.append(domain["DomainName"])
    # Prompt user to pick which domains they want
    domains = Check(
        "Which domains would you like to update? (Press space to (de)select a domain)", 
        choices=domain_list,
    ).launch()
    print("\nYou selected:")
    for d in domains:
        print(d)
    print("\n")
    return domains


def get_full_contact_details():
    contact_info = VerticalPrompt(
        [
            Input("First Name: "),
            Input("Last name: "),
            Bullet(
                prompt = "Choose a contact type from the items below: ", 
                choices = ['PERSON', 'COMPANY', 'ASSOCIATION', 'PUBLIC_BODY', 'RESELLER'],
                **styles.Ocean
            ),
            Input(
                "Organization name (Used when contact type is not a person): ", 
                pattern=".*"
            ),
            Input("Address Line 1: "),
            Input("Address Line 2: "),
            Input("City: "),
            Input("State: "),
            Input(
                "Two Digit Country Code (e.g. US, GB, JP): ",
                pattern="^[A-Z]{2}$"),
            Input("Zip Code: "),
            Input(
                "Phone Number with period after country code (e.g. for United States: +1.5556667788): ",
                pattern="^\+[0-9]{1,2}\.[0-9]{10}$"
            ),
            Input("Email: ")
        ],
        spacing = 1
    ).launch()
    details = {
        'FirstName': contact_info[0][1],
        'LastName': contact_info[1][1],
        'ContactType': contact_info[2][1],
        'AddressLine1': contact_info[4][1],
        'AddressLine2': contact_info[5][1],
        'City': contact_info[6][1],
        'State': contact_info[7][1],
        'CountryCode': contact_info[8][1],
        'ZipCode': contact_info[9][1],
        'PhoneNumber': contact_info[10][1],
        'Email': contact_info[11][1],
    }
    if details['ContactType'] != "PERSON":
        details["OrganizationName"] = contact_info[3][1]
    return details


def get_address_change_details():
    address_info = VerticalPrompt(
        [
            Input("Address Line 1: "),
            Input("Address Line 2: "),
            Input("City: "),
            Input("State: "),
            Input(
                "Two Digit Country Code (e.g. US, GB, JP): ",
                pattern="^[A-Z]{2}$"),
            Input("Zip Code: "),
        ],
        spacing = 1
    ).launch()
    details = {
        'AddressLine1': address_info[0][1],
        'AddressLine2': address_info[1][1],
        'City': address_info[2][1],
        'State': address_info[3][1],
        'CountryCode': address_info[4][1],
        'ZipCode': address_info[5][1],
    }
    return details


def update_domains(selected_domains, contact_details):
    # Show the domains and details and have the user confirm
    print("Your contact information will be updated to the following: ")
    print("\n")
    pprint(contact_details)
    print("\n")
    if not YesNo("Does the above look correct? (y/n) ").launch():
        print("Ok! Go ahead and try again.")
        return
    print("The domains to be updated are: ")
    for domain in selected_domains:
        print(domain)
    print("\n")
    if not YesNo("Does the above look correct? (y/n) ").launch():
        print("Ok! Go ahead and try again.")
        return
    for domain in selected_domains:
        print(f"Updating {domain}")
        r53domains.update_domain_contact(
            DomainName=domain,
            AdminContact=contact_details,
            RegistrantContact=contact_details,
            TechContact=contact_details
        )
        time.sleep(4)

def is_address_only_update():
    address_only = VerticalPrompt(
        [
            Bullet(
                prompt = "Would you like to update domain address(es) to the same new address?", 
                choices = ['YES', 'NO'],
                **styles.Ocean
            ),
        ]
    ).launch()
    if address_only[0][1] == "YES":
        return True
    else:
        return False


def update_domain_addresses(domains):
    change_details = get_address_change_details()
    fields = ['AddressLine1', 'AddressLine2', 'City', 'State', 'CountryCode', 'ZipCode']
    for domain in domains:
        detail = r53domains.get_domain_detail(DomainName=domain)
        admin_contact = detail['AdminContact']
        registrant_contact = detail['RegistrantContact']
        tech_contact = detail['TechContact']
        for f in fields:
            admin_contact[f] = change_details[f]
            registrant_contact[f] = change_details[f]
            tech_contact[f] = change_details[f]
        print(f"Updating {domain}")
        r53domains.update_domain_contact(
            DomainName=domain,
            AdminContact=admin_contact,
            RegistrantContact=registrant_contact,
            TechContact=tech_contact
        )
        time.sleep(4)

def main():
    domains = get_user_picked_domains_to_change()
    if is_address_only_update():
        print("Reviewing domains...")
        print("Collecting details...")
        update_domain_addresses(domains)
        print("Address(es) Updated!")
    else:
        details = get_full_contact_details()
        update_domains(domains, details)
        print("Domain contact details updated!")

if __name__ == "__main__":
    main()
