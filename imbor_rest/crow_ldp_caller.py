import datetime
import uuid
import hashlib
import hmac
import base64
from requests import Request, Session
import urllib.parse


class CrowLdp:
    def __init__(self, clientId, toolId, privateKey, base_url):
        self.clientId = clientId
        self.toolId = toolId
        self.privateKey = privateKey
        self.base_url = base_url

        # print("clientId: " + str(self.clientId))
        # print("toolId: " + str(self.toolId))
        # print("privateKey: " + str(self.privateKey))
        # print("base_url: " + str(self.base_url))

    # Functie om de HMAC signature te berekenen, zie documentatie van CROW voor de benodigde parameters
    def get_hmac(self, req, url):
        # Timestamp (op secondes, afgesloten met een 'Z')
        currentDate = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        # Random GUID conform RFC 4122
        nonce = str(uuid.uuid4())

        # Afhankelijk van een GET of POST request is het signature anders
        method = req.method
        message = method + "," + currentDate + "," + url + "," + nonce

        if method == "POST":
            contentType = req.headers["Content-Type"]
            body = req.data
            if len(body) > 0:
                md5 = hashlib.md5(req.data.encode("utf-8")).hexdigest()
                message += "," + contentType + "," + md5

        # print(message)
        value = bytes(message, "utf-8")
        # privateKey wordt eerder in het notebook opgehaald, net als clientId
        privkey = bytes(self.privateKey, "utf-8")

        hashBase64 = base64.b64encode(
            hmac.new(privkey, value, digestmod=hashlib.sha256).digest()
        )
        authorization = (
            'HMAC clientId="'
            + self.clientId
            + '", nonce="'
            + nonce
            + '", currentDate="'
            + currentDate
            + '", signature="'
            + hashBase64.decode("utf-8")
            + '"'
        )

        return authorization

    # helper functie om het request te doen
    def run_query(self, payload):
        s = Session()
        url = self.base_url
        querystring = {"output": "json", "toolid": self.toolId, "trace": "namespaces"}
        url = str(url) + "?" + urllib.parse.urlencode(querystring)

        req = Request("POST", url, data=payload)
        headers = {"Content-Type": "application/sparql-query"}
        req.headers = headers
        auth = self.get_hmac(req, url)
        # print(auth)
        headers = {"Authorization": auth, "Content-Type": "application/sparql-query"}
        req.headers = headers
        prepared = req.prepare()
        response = s.send(prepared)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                "Query failed to run by returning code of {}. {}".format(
                    response.status_code, response.text
                )
            )
