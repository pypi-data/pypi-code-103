from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials


def create_keyfile_dict():
    variables_keys = {
        "type": "service_account",
        "project_id": "kursversorgung-warrants",
        "private_key_id": "001902bc3d2b4f52449dabdbd024b0634634db90",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC56DxGENrwtw6y\naxFb1qPcdKTTnzqImbl9EUfLZLcz1EccuUuieXefTzB9uECe43Z25AsNXCImq1M0\npEGLfOS+EN54E6jocf5ccGOMiafUCUgbeX43IPiI8nakDpkrn8uOsMA0Vxd0yPdY\nzZmJMXC6LbOi+2ISGQCpWSg4XWKwMnhsrnZuUXGJDBLWEdfmZoQOh9XSnHJSDAcm\n+cnT0wDMW5+IVIAvcBgc8Vg1mwX8OFARZIl+d9kRZp2/wtvSZJe4fn7BN3B3UMRr\n/ykA9bY7EiXutb4O6do81D9GbKkOQfze9CKt+uRhZBesyToBLeh0HCiYtJv35VlF\nIzqR2iZ3AgMBAAECggEAUpGKX6Yxz5LGRMkX8x2wNoRaBqGkWjJId3ta00O+uJbS\nJLhJlvZzAj8mLthMXyVwoppjLEJc6qbSNEG12NGWOLJ+VH+K1/51NjI2jJ9A+oRK\n0eUSgUK0EAL8XZ4cOotk2dG39CcwRE7TyM28IPpj8lTFAaC77ITNTenK2snjQJTP\nfTsO3ZU4qD3+hs4LY610xJ9Jslsy7aspDPkBL4zP1oM8jz1mX2hMr1megVs3iqzr\n3XDMdXCpT60PXRUi0oUx8DLHT/9MnEaDvykwmFLtzEjKjdOT++9sgdQ6fk4GAnJr\nLlZbP6EWqI6kCZ2r5R9WYcOiiPoa+MnIvnhrLZ0ENQKBgQDtU+HM5RaokSSMON2s\nKpkH0txYcPnG6kuMIzGwBn2Z0gZSZzYobABi3+i5B51oS6gh7AJ+KnjIZL3UdgLB\noGmczPBh0no4LX8hf3Szr6+zJyPE0LzSwcExA54OHAXZ9uLY/S0bxCcarIvCnbdI\n6IueaHP1U3hu0ZCsLEaRtthPUwKBgQDIiKvWqXDEO4uYCei/a+JO0cp9QcoqUo0A\nZfkGoOff+fVxsdlhX6a/BGHsRbV0OyjG+2lxFF9UE4SOFDlgkAHl1Kjtx72/IwTK\n0QWbl9b/CyGJbGekD9mM96W8apQVMAUs1l65/hnmJMs0dT+VUEcbccVjYMZ7epI+\nwwV/b2u7zQKBgCYZdkFncZjEHELqiiOufvyzjC4ijOazDEfGCp8Am79K6TrnWNlq\nZTF6UqkJoOpyYt53Pfs1JEi/a34lJ9Ifx3Slrd12ZaqJG0SsanbCOImhOevJutZ2\nxmXw97m6I/JW4RoGouw3NDPjCVjH6vmoY2mdySfUK5xWxkvtm7Ke0OEDAoGALvc7\nb7INdBgSEJC5jyOARD+EMiPXamQdG+vGEBRdWiqbnn4t0E1rqy8mlASbg9ZbLYcy\nYcaIsRNFJ1V7Pq9bkm1lBxOR0BMuiyW7L363XtJHj3zxJQ6FQCu8CE3Z0sCFZcPr\nOZpWjH0vjmCrfJfpn3bc6PKAaekCGWrpfbglvj0CgYAlfUjvtHKHqgKCkca/3Ssq\njawqSls4C4hvRIzRnI+F0Z9fR/dFXd/PY3xVrU9O4B1KiiFaK8INzZkKTg4dKC86\n+L2vgmVbaMOWI81I86iO6VCJd4lQ96WZkyCtZrCFZ+6XmQTxM8tZ5msG4gEZkeEP\n6IkwP+9XHEyJe0IN74WZ/g==\n-----END PRIVATE KEY-----\n",
        "client_email": "autoupdate@kursversorgung-warrants.iam.gserviceaccount.com",
        "client_id": "112479920726975497823",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/autoupdate%40kursversorgung-warrants.iam.gserviceaccount.com"
    }
    return variables_keys


def create_client_with_scope():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)

    return authorize(creds)
