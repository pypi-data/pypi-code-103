import boto3
import time

from bullet import Input, VerticalPrompt, Check, YesNo

mailman_ascii = """
   _______________
  /   \           \\
 /     \   .=====. \\
/      |   |_____|  \\
|      |            |         Welcome to AWS Mailman:
|      |   ________ |
|      |  /  aws  / |      An easy way to update the addresses 
|      | /mailman/  |         on all your Route53 Domains!
|      | --------   |
|      |            |
|  _   |  _ ______  |
|_/ \  | | |      | |
     |_|_| |      | |
"""

ADDRESS_FIELDS = ['AddressLine1', 'AddressLine2', 'City', 'State', 'CountryCode', 'ZipCode']


r53domains = boto3.client('route53domains')

def get_user_picked_domains_to_change():
    # List Route 53 domains
    response = r53domains.list_domains()
    domain_list = []
    for domain in response["Domains"]:
        domain_list.append(domain["DomainName"])
    domain_string_prompt = (
        "Which domains would you like to update?\n"
        "(Press space to (de)select a domain and Enter when finished)\n"
    )
    domains = Check(
        prompt=domain_string_prompt,
        choices=domain_list,
    ).launch()
    print("\nYou selected:")
    for d in domains:
        print(d)
    print("\n")
    return domains


def get_address_change_details():
    address_info = VerticalPrompt(
        [
            Input("🏠 Address Line 1: "),
            Input("🏠 Address Line 2 (Just put a space here if you don't have a line 2): "),
            Input("🏙️ City: "),
            Input("🏔️ State: "),
            Input(
                "🏳️ Two Digit Country Code (e.g. US, GB, JP): ",
                pattern="^[A-Z]{2}$"),
            Input("📬 Zip Code: "),
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


def update_domain_addresses(domains):
    change_details = get_address_change_details()
    for domain in domains:
        detail = r53domains.get_domain_detail(DomainName=domain)
        admin_contact = detail['AdminContact']
        registrant_contact = detail['RegistrantContact']
        tech_contact = detail['TechContact']
        for f in ADDRESS_FIELDS:
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

def run_guidance():
    if YesNo("Want help or some basic info about this tool? Default: ").launch():

        print("\nThis tool will help you update your Route53 domain addresses.")
        print("")
        print("Note: Because changing your contact name requires additional steps,")
        print("this tool will keep the same contact name, organization type, and")
        print("other fields for all domains. The only thing updated is the address you provide.")
        print("\nThis includes: ")
        for field in ADDRESS_FIELDS:
            print(f"    {field}")
        print("\nBasic usage will be for you to select the domains you want to update,")
        print("and then enter your updated address with the information above.\n")
        print("\nBasic requirements and common mistakes:\n")
        print("    - Make sure your AWS CLI credentials are configured correctly.")
        print("    - Make sure you're using the right AWS CLI profile.")
        print("    - Make sure that you have the correct permissions to update the domain.")
        print("    - Make sure to make a PR if you see any bugs or issues 😊:")
        print("      https://github.com/fernando-mc/aws-mailman/issues")
        if not YesNo("Ready to continue? Default: ").launch():
            exit()
        print("\n")


def main():
    print(mailman_ascii)
    run_guidance()
    domains = get_user_picked_domains_to_change()
    update_domain_addresses(domains)
    print("Address(es) Updated!")

if __name__ == "__main__":
    main()
