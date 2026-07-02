import urllib.parse
import urllib.request
import json
import time
import csv

input_file = "queries.json"
output_file = "queries_result.csv"

with open(input_file, "r", encoding="utf-8") as file:
    queries = json.load(file)
    rows = []

for category, inquiries_list in queries.items():
    for inquire in inquiries_list:
        print(category, "-->", inquire)

        params = {
            "q": inquire,
            "format": "json",
            "limit": 1,
            "viewbox": "-64.50,-33.00,-64.20,-33.30" ,
            "bounded": 1
        }
        
        query_string = urllib.parse.urlencode(params)
        url = "https://nominatim.openstreetmap.org/search?" + query_string
        
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "TransitAR-Research/1.0"})
            response = urllib.request.urlopen(request, timeout=10)
            raw_data = response.read()
        
            result = json.loads(raw_data.decode("utf-8"))

            if not result:
                rows.append([category, inquire, None, None, "NO_RESULT"])
            else:
                top = result[0]
                lat = float(top["lat"])
                lon = float(top["lon"])
                display_name = top["display_name"]
                rows.append([category, inquire, lat, lon, display_name])
                
        except Exception as error:
            print("Error on query:", inquire, "-->", error)
            rows.append([category, inquire, None, None, f"ERROR: {error}"])

        time.sleep(1)

with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
    try:
        writer = csv.writer(csv_file)
        writer.writerow(["category", "query", "lat", "lon", "display_name"])
        writer.writerows(rows)
    except Exception as error:
        print("Error writing in output file:", error)
    else:
        print("Results written in:", output_file)
    

