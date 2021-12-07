import requests as r
import json


class ShipRocket:
    def __init__(self, email=None, password=None):
        if email and password:
            self.email = email
            self.password = password

            auth_token_url = "https://apiv2.shiprocket.in/v1/external/auth/login"
            payload = {"email": email, "password": password}
            headers = {"Content-Type": "application/json"}
            response = r.request(
                "POST",
                auth_token_url,
                headers=headers,
                data=json.dumps(payload),
                allow_redirects=False,
            )

            resp = response.json()
            self.company_id = resp["company_id"]
            self.auth_token = resp["token"]
            self.header=headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.auth_token),
                                   }

    def get_balance(self):
                url="https://apiv2.shiprocket.in/v1/external/account/details/wallet-balance"
                resp = r.get(url, headers=self.header, allow_redirects=False)
                return resp.json()



    def get_all_pickup_address(self):
        url = 'https://apiv2.shiprocket.in/v1/external/settings/company/pickup'
        resp = r.get(url, headers=self.header, allow_redirects=False)
        if resp.status_code == 200:
            return resp.json()['data']['shipping_address']
        else:
            return False

    def add_pickup_address(self,location_nickname,name,email,phone,address_lin1,address_line2,city,state,country,pin_code):
       try:
           url = 'https://apiv2.shiprocket.in/v1/external/settings/company/addpickup'
           payload = {"pickup_location": location_nickname, "name": name, "email": email, "phone": phone,
                      "address": address_lin1, "address_2": address_line2, "city": city, "state": state,
                      "country": country, "pin_code": pin_code}
           resp = r.post(url, headers=self.header, json=payload, allow_redirects=False)
           if resp.status_code == 200:
               return resp.json()['address']
           return resp.json()
       except Exception as e:
           return str(e)
    def check_service_availabe(self,pickup_pincode,delivery_pincode,weight=.5,cod=False):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/courier/serviceability/'
            payload = {"pickup_postcode":pickup_pincode,"delivery_postcode":delivery_pincode,"weight":weight,"cod":cod}
            resp = r.get(url, headers=self.header, json=payload, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()['data']['available_courier_companies']
            return resp.json()
        except Exception as e:
            return str(e)

    def create_shoppment(self,**kwargs):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/orders/create/adhoc'
            resp = r.post(url, headers=self.header, json=kwargs, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)
    def cancel_shippment(self,order_ids):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/orders/cancel'
            payload={'id':order_ids.split(",")}
            resp = r.post(url, headers=self.header, json=payload, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)

    def generate_awp_shippment(self,shipment_id,courier_id=None):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/courier/assign/awb'
            payload={}
            if courier_id != None:
                payload['courier_id']=courier_id
            payload['shipment_id']=shipment_id
            resp = r.post(url, headers=self.header, json=payload, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)

    def pickup_request(self,shipment_id):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/courier/generate/pickup'
            payload={}
            payload['shipment_id']=shipment_id
            resp = r.post(url, headers=self.header, json=payload, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)

    def get_all_shipment(self):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/orders'

            resp = r.get(url, headers=self.header, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()['data']
            return resp.json()
        except Exception as e:
            return str(e)
    def get_shipment(self,order_id):
        try:
            url = f'https://apiv2.shiprocket.in/v1/external/orders/show/{order_id}'

            resp = r.get(url, headers=self.header, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()['data']
            return resp.json()
        except Exception as e:
            return str(e)

    def generate_mainfest(self,shipment_id):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/manifests/generate'
            payload={}
            payload['shipment_id']=shipment_id.split(",")
            resp = r.post(url, headers=self.header, json=payload, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)

    def generate_label(self, shipment_id):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/courier/generate/label'
            payload = {}
            payload['shipment_id'] = shipment_id.split(",")
            resp = r.post(url, headers=self.header, json=payload, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)

    def create_shippment_with_download_label(self,**kwargs):
        try:
            url = 'https://apiv2.shiprocket.in/v1/external/shipments/create/forward-shipment'
            resp = r.post(url, headers=self.header, json=kwargs, allow_redirects=False)
            if resp.status_code == 200:
                return resp.json()
            return resp.json()
        except Exception as e:
            return str(e)





a=ShipRocket("ankit@jaakhoo.com","1232245895")

# a.add_pickup_address("moradabad","sweta bhardwaj","ankitbhardwaj007@gmail.com","7065044493","lig d 62 himgiri colony ","Kanth Road","Moradabad","Uttar Pradesh","India","244001")
# print(a.get_all_pickup_address())
# print(a.check_service_availabe(244001,201001))
print(a.generate_awp_shippment("a","b"))