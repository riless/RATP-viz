import json
import csv

fields = ["age", "area", "priceSquare", "singles", "married", "retired", "students", "unemployment", "income", "tax", "highDiploma", "permanentResidence", "secondResidence", "owners", "tenants"]
json_filename = "data.json"
data = json.load( open(json_filename, 'r') )
for field in fields:
	out = []
	for arr,d in data["districts"].items():
		if ( int(arr) <= 20):
			out.append( [ d['name'], d[field] ] )

	with open('output/'+field+'.csv', "wb") as csv_file:
		open_file_object = csv.writer(csv_file)
		open_file_object.writerow(["name",field])
		open_file_object.writerows(out)
		csv_file.close()

