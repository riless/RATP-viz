import csv
import pickle as pk 



with open(r"data/u10kSt.pkl", "rb") as pk_file:
	usagers = pk.load(pk_file)
 
# usagers_ids = list( set( [ usagers_id for usagers_id, _ in usagers ] ))

# print usagers[0]

# with open('usagers.csv', 'w') as csvfile:
#     fieldnames = ['usager_id']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()
#     for usager_id in usagers_ids:
#         writer.writerow( {'usager_id': usager_id} )


with open('passages.csv', 'w') as csvfile:
    fieldnames = ['passage_id', 'passage_time', 'station_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    
    for passage_id, passages in usagers:
       for passage_time, station_id in passages: 
            row = {
                'passage_id': passage_id,
                'passage_time': passage_time,
                'station_id': station_id,
            }
            writer.writerow( row )

