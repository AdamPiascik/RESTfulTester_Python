import argparse
import requests
import json
import os

# ----------------------------------------------------------------------

def ParseArgs():
    parser = argparse.ArgumentParser(description="Tool for generating CSV\
                     files containing the full set of information needed to\
                     test all endpoints of a RESTful API.",
                                    prog='TestAPI')
    parser.add_argument("url",
                        help="The base URL of the API you want to test",
                        type=str)
    parser.add_argument("-a", "--auth",
                        metavar="",
                        help="Specifies a list of endpoints that provide\
                        authorization credentials. These will be called first\
                        to generate access tokens for relevant endpoints.",
                        action="append",
                        dest="auth",
                        type=str)
    parser.add_argument("-p", "--parametersFile",
                        metavar="",
                        help="Specifies the JSON file containing dummy\
                        data. This data will be use to populate the required\
                        parameters for relevant endpoints.",
                        dest="parametersFile",
                        type=str)
    parser.add_argument("-v", "--version",
                        metavar="",
                        help="The version of the API you are testing.\
                        The default value is 1.",
                        dest="version",
                        type=int,
                        default=1,)
    try:
        args = parser.parse_args()
        return args
    except:
        return

# ----------------------------------------------------------------------

def GetParametersForEndpoint(requestedEndpoint, parameters_file):
    if parameters_file is not None:
        with open(parameters_file, 'r') as jsonData:
            endpoints = json.load(jsonData)
            for endpoint, parameters in endpoints.items():
                if endpoint == requestedEndpoint:
                    return parameters

def ParseParameters(requestedEndpoint, parameters_file):
    dict = GetParametersForEndpoint(requestedEndpoint, parameters_file)
    params = ""
    if dict is not None:
        for key, value in dict.items():
            params += (key + "=" + str(value) + ";")
        return params[:-1]
    return params

def GetAllAccessTokens(baseurl, auth_endpoints, parameters_file):
    access_tokens = {}
    for auth in auth_endpoints:
        with requests.post(baseurl + auth, json=
        GetParametersForEndpoint(auth, parameters_file))as response:
            try:
                access_tokens[auth] = response.json()["access_token"]
            except:
                print("Authorization failed for" + auth)
    return access_tokens

def GetAccessTokenForEndpoint(endpoint_description, access_tokens):
    identifier = "auth="
    start = endpoint_description.find(identifier)
    if start != -1:
        if endpoint_description.find(" ", start) != -1:
            end = endpoint_description.find(" ", start)
        else:
            end = len(endpoint_description)
        auth_endpoint = endpoint_description[start + len(identifier) : end]
        try:
            return access_tokens[auth_endpoint]
        except:
            return ""
    return ""

# ----------------------------------------------------------------------

def main():
    args = ParseArgs()
    baseurl = args.url
    auth_endpoints = args.auth
    parameters_file = args.parametersFile
    version = str(args.version)

    sanitised_url = baseurl.replace("https://", "").replace("http://", "").replace("/", "")

    with requests.get(baseurl + "/v" + version + "/doc.json") as url:
        doc_file = url.json()

    if auth_endpoints:
        access_tokens = GetAllAccessTokens(baseurl, auth_endpoints, parameters_file)

    endpoint_details = []
    for endpoint, methods in doc_file["paths"].items():
        for method, data in methods.items():
            try:
                token = GetAccessTokenForEndpoint(data["description"], access_tokens)
            except:
                token = ""
            line = ",".join([endpoint, method, token, ParseParameters(endpoint, parameters_file)])
            endpoint_details.append(line)

    filename = os.path.join("."
                            ,sanitised_url
                            +version + ".csv")

    with open(filename, "w") as file:
        for item in endpoint_details:
            file.write(item + "\n")

# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
