import requests
import json


class washstation():
    def __init__(self, user:dict, debug:bool=False) -> None:
        # login data
        self.loginData = {'username':user["username"],
                      'password':user["password"],
                      'client_id':user["client_id"],
                      'client_secret':user["client_secret"],
                      'grant_type':'password'
        }

        # refresh data
        self.refreshData = {'refresh_token':'',
                        'client_id':user["client_id"],
                        'client_secret':user["client_secret"],
                        'grant_type':'refresh_token'
        }

        # content of the header that is present in all communications
        self.universal_header = {'Host':'mobile.kosmoshub.com',
                                 'Device':user["Device"],
                                 'Content-Type':'application/x-www-form-urlencoded',
                                 'Accept':'*/*',
                                 'Connection':'keep-alive',
                                 'Locale':'en',
                                 'Accept-Language':'en-US,en;q=0.9',
                                 'Accept-Encoding':'gzip, deflate, br',
                                 'User-Agent':'Washstation/788 CFNetwork/1390 Darwin/22.0.0'
        }

        # locally stored tokens and session id
        self.refresh_token = ""
        self.access_token = ""
        self.session_id = ""
        self.location = "-1"

        # data about washers
        self.washers = {}
        self.washers_available = {}

        # display more data about communications
        self.debug = debug


    def login(self) -> bool:
        '''
        # login
        '''

        print(f"[API] - Logging in as {self.loginData['username']}")

        # request to login as a user
        response = requests.post(url='https://mobile.kosmoshub.com/washstation/oauth/v2/token', data=self.jsonToRequest(self.loginData), headers=self.universal_header)
        response = json.loads(response.content.decode("utf-8"))

        # display response
        self.printResponse(response=response)

        # update refresh token and access token
        if "refresh_token" in response.keys() and "access_token" in response.keys():
            self.refresh_token = response["refresh_token"]
            self.access_token = response["access_token"]

            # success
            return True
        else:

            # failure
            return False


    def refresh(self) -> bool:
        '''
        # refresh
        '''

        print("[API] - Refreshing")

        # create copy of refresh request and add local token
        refresh = self.refreshData
        refresh["refresh_token"] = self.refresh_token

        # if refresh token is available to use
        if self.refresh_token:

            # request an extended session
            response = requests.post(url='https://mobile.kosmoshub.com/washstation/oauth/v2/token', data=self.jsonToRequest(refresh), headers=self.universal_header)
            response = json.loads(response.content.decode("utf-8"))

            # display result
            self.printResponse(response=response)

            # update refresh token and access token
            if "refresh_token" in response.keys() and "access_token" in response.keys():
                self.refresh_token = response["refresh_token"]
                self.access_token = response["access_token"]
                
                # success
                return True
            else:

                # failure
                return False
        else:

            # failure
            return False


    def getProfile(self) -> None:
        '''
        # getProfile
        '''

        print("[API] - Acquiring profile details")

        # create header from template
        header_copy = self.universal_header
        header_copy.setdefault("Authorization", f"Bearer {self.access_token}")

        # request profile details
        response = requests.get(url='https://mobile.kosmoshub.com/washstation/api/profile', headers=header_copy)
        response = json.loads(response.content.decode("utf-8"))

        # update default location
        self.location = response["default_location_id"]

        # display result
        self.printResponse(response=response)


    def getWashers(self) -> bool:
        '''
        # getWashers
        '''

        print("[API] - Getting washers")

        # reset variables
        self.washers = {}
        self.washers_available = {}

        # create header from template
        header_copy = self.universal_header
        header_copy.setdefault("Authorization", f"Bearer {self.access_token}")
        header_copy.setdefault("Location", self.location)

        # start a session
        response = requests.post(url='https://mobile.kosmoshub.com/washstation/api/checkout/start-session', headers=header_copy)
        response = json.loads(response.content.decode("utf-8"))

        # display result
        self.printResponse(response=response)

        # if session established succesfully load all of the washer details
        if "success" in response.keys():
            # update session id
            self.session_id = response["sessionId"]
            header_copy.setdefault("Session", self.session_id)

            # request data about washers
            response2 = requests.get(url='https://mobile.kosmoshub.com/washstation/api/catalog/machines/1', headers=header_copy)
            response2 = json.loads(response2.content.decode("utf-8"))


            for i in response2:
                self.washers.setdefault(i["name"], i["id"])
                self.washers_available.setdefault(i["id"], i["isAvailable"])
                self.printResponse(response=i)
            return True
        else:
            return False


    def getCart(self) -> None:
        '''
        # getCart
        '''

        print("[API] - Getting cart")

        # make a copy of the template header
        header_copy = self.universal_header
        header_copy.setdefault("Authorization", f"Bearer {self.access_token}")
        header_copy.setdefault("Location", "55")
        header_copy.setdefault("Session", self.session_id)

        # request cart details
        response = requests.get(url='https://mobile.kosmoshub.com/washstation/api/checkout/cart', headers=header_copy)
        response = json.loads(response.content.decode("utf-8"))

        # display result
        self.printResponse(response=response)
    

    def reserveWasher(self, id:int=-1) -> bool:
        '''
        # reserveWasher
        '''

        print(f"[API] - Reserving {[i for i in self.washers.keys][[i for i in self.washers.value()].index(id)]}")

        # create copy of header template
        header_copy = self.universal_header
        header_copy.setdefault("Authorization", f"Bearer {self.access_token}")
        header_copy.setdefault("Location", "55")
        header_copy.setdefault("Session", self.session_id)

        # check if washer is actually available
        if id in self.washers.values() and self.washers_available[id]:
            
            # make a booking
            response = requests.post(url=f'https://mobile.kosmoshub.com/washstation/api/checkout/make-booking/{id}', headers=header_copy)
            response = json.loads(response.content.decode("utf-8"))

            # display result
            self.printResponse(response=response)

            # success
            return True
        else:

            # failure
            return False


    def jsonToRequest(self, dictionary):
        '''
        # jsonToRequest
        '''
        # tmp variable
        final = ""

        # append concatenated string
        for key, value in zip(dictionary.keys(), dictionary.values()):
            final += key + "=" + value + "&"

        # remove the additional '&' symbol at the end
        return final[:-1]


    def printResponse(self, response):
        # show if debug mode is on
        if self.debug:

            # iterate over the responses keys and values and display
            for key, value in zip(response.keys(), response.values()):
                print(f"{key} : {value}")

            # prettier this way
            print("\n")


# if __name__ == "__main__":
#     # details the api uses to connect to the server
#     details = {"username":"",
#                "password":"",
#                "client_id":"",
#                "client_secret":"",
#                "Device":""
#     }

#     # create an instance of the api class
#     wash = washstation(user=details, debug=True)

#     # test functions and their responses
#     wash.login()
#     wash.refresh()
#     wash.getProfile()
#     wash.getWashers()
#     wash.getCart()

#     # test responses and print out available washers
#     wash.printResponse(response=wash.washers)
#     wash.printResponse(response=wash.washers_available)
