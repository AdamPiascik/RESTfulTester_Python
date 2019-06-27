import argparse
import requests
import json
import os

# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Tool for generating CSV\
                     files containing the full set of information needed to\
                     test all endpoints of a RESTful API.",
                                    prog='TestAPI')
    parser.add_argument("url",
                        help="The base URL of the API you want to test",
                        type=str)
    parser.add_argument("-p", "--parameters",
                        metavar="",
                        help="Specifies the JSON file containing dummy\
                        data. This data will be use to populate the required\
                        parameters for relevant endpoints.",
                        dest="parameters",
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
    except:
        return

# ----------------------------------------------------------------------

    sanitised_url = args.url.replace("https://", "").replace("/", "")
    version = "-v" + str(args.version)
    format = ".json"

    with requests.get(args.url + "/v" + str(args.version) + "/doc.json") as url:
        doc_file = url.json()


    def GetParametersForEndpoint(requestedEndpoint):
        if args.parameters is not None:
            with open(args.parameters, 'r') as jsonData:
                endpoints = json.load(jsonData)
                for endpoint, parameters in endpoints.items():
                    if endpoint == requestedEndpoint:
                        return parameters

    def ParseParameters(requestedEndpoint):
        dict = GetParametersForEndpoint(requestedEndpoint)
        params = ""
        if dict is not None:
            for key, value in dict.items():
                params += (key + "=" + str(value) + ";")
            return params[:-1]
        return params

    list_endpoints = []
    for endpoint, methods in doc_file["paths"].items():
        for method, data in methods.items():
            line = ",".join([endpoint, method, ParseParameters(endpoint)])
            list_endpoints.append(line)

    filename = os.path.join("."
                            ,sanitised_url
                            +version + ".csv")

    with open(filename, "w") as file:
        for item in list_endpoints:
            file.write(item + "\n")

# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
