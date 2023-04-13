from pya3 import *
import hashlib

api_key = "YC7ScQBtPe71YUOJ5mWbQcn9V6CHu891ZnJE13J2T7IHSW3cQMHFPKiYUsZqhdTsxMs5GNRr7WUaWVjyGPrEf7E03evOAmqAg6SiNLzNGSV20tUom1UmTDrMLqblYlKM"

session_id = "88VqXVxlnL6lQCXHJW5cxU91k285A82soYKBBT8NOYUEhAlMpxDJX2eByFr6eM3sa2pmZzOC9XOu7g8i5hFsTlCuYoGRedWsAgf5Mo6gcYGjPno0l4JMqmVqsc0CisSTzdcb9VX3J5FkLtAVvgacX7vNRhWG8qzj7OQpZF3WdbLZP4oaVDnQm90A2dYM1YgsQqGk5gixW4GsgGV5AA6XtQQy29xJTaYlEnD7GTGkjUVsJmYx2C6OEMfFxpfouYXP"


user_id = "860288"
alice = Aliceblue(user_id='860288',api_key=api_key)

auth_code = "NGIJWC937R60WAVXM79R"

#print(alice.get_session_id())

# from alice_blue import *

# session_id = AliceBlue.login_and_get_sessionID(   username    = "860288", 
#                                                     password    = "Sree@123", 
#                                                     twoFA       = "1986",
#                                                     app_id      = "app_id",
#                                                     api_secret  = "YC7ScQBtPe71YUOJ5mWbQcn9V6CHu891ZnJE13J2T7IHSW3cQMHFPKiYUsZqhdTsxMs5GNRr7WUaWVjyGPrEf7E03evOAmqAg6SiNLzNGSV20tUom1UmTDrMLqblYlKM")

# print(session_id, " session_id")

encKey = "JEWK4DJOVJQN3EL0DHPAAAVEUD5SOLQG"



import requests
import json
bas_url = "https://ant.aliceblueonline.com/rest/AliceBlueAPIService/api/"
# url = bas_url+"customer/getAPIEncpkey"
# payload = json.dumps({
#   "userId": user_id,
# })
# headers = {
#   'Content-Type': 'application/json'
# }
# response = requests.request("POST", url, headers=headers, data=payload)
# print(response.text)


result = hashlib.sha256((user_id+api_key+encKey).encode(encoding='UTF-8',errors='strict'))

url = bas_url+"customer/getUserSID"
payload = {
  "userId": user_id,
  "userData": "fc0270caecf7768db436263d222411fd77ce10b33d3e05c1b2a9b1a924630038"
}
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
