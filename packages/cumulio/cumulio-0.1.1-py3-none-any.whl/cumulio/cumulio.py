import requests
import json

class Cumulio(object):
    def __init__(self, api_key, api_token):
        if not api_key or type(api_key) is not str:
            raise Exception("Please provide a valid API Key of type str")
        if not api_token or type(api_token) is not str:
            raise Exception("Please provide a valid API Token of type str")
        print("initializing cumulio client...")
        self.api_key = api_key
        self.api_token = api_token
        self.APP = "https://app.cumul.io"
        self.HOST = "https://api.cumul.io"
        self.PORT = 443
        self.VERSION = "0.1.0"
    
    def help(self):
        print("Use this Python SDK to create and maintain Cumul.io securables")

    def create(self, resource, properties, associations = {}):
        query = {}

        query["action"]         = "create"
        query["properties"]     = properties
        query["associations"]   = associations

        return self.__emit(resource, "POST", query)
    
    def get(self, resource, filter):
        query = {}
        
        query["action"] = "get"
        query["find"]   = filter
        return self.__emit(resource, "SEARCH", query)

    def delete(self, resource, id, properties = {}):
        query = {}
        
        query["action"]     = "delete"
        query["id"]         = id
        query["properties"] = properties
        return self.__emit(resource, "DELETE", query)

    def update(self, resource, id, properties = {}):
        query = {}

        query["action"]     = "update"
        query["id"]         = id
        query["properties"] = properties
        return self.__emit(resource, "PATCH", query)

    def associate(self, resource, id, association_role, association_id, properties = {}):
        query       = {}
        association = {}

        association["role"] = association_role
        association["id"]   = association_id
        query["action"]     = "associate"
        query["id"]         = id
        query["resource"]   = association
        query["properties"] = properties
        return self.__emit(resource, "LINK", query)
    
    def dissociate(self, resource, id, association_role, association_id):
        query       = {}
        association = {}

        association["role"] = association_role
        association["id"]   = association_id
        query["action"]     = "associate"
        query["id"]         = id
        query["resource"]   = association
        return self.__emit(resource, "UNLINK", query)       

    def query(self, filter = {}):
        return self.get("data", filter)

    def iframe(self, dashboard_id, authorization):
        return self.APP + "/i/" + dashboard_id + "?key=" + authorization["id"] + "&token=" + authorization["token"]

    def __emit(self, resource, action, query):
        query["key"]        = self.api_key
        query["token"]      = self.api_token
        query["version"]    = self.VERSION

        url = self.HOST + ':' + str(self.PORT) + '/' + self.VERSION + '/' + resource
        try:
            response = requests.post(url, headers = {'Content-Type':'application/json'}, data = json.dumps(query))
        except:
            print("Something went wrong, please try again later")
        if not response.ok:
            raise Exception(response.reason + ": " + response.json()["message"])
        return response.json()  
