"""
program: dedupe_political_donations.py
author: Kostiantyn Makrasnov
date: 05/13/2021
purpose: find clusters of similar rows in the political donations dataset, then
combine all of the rows
"""

# Import needed packages for analysis
import pandas as pd
import numpy as np
import os
import csv
import dedupe


# Filters the original dataset
# - (1) Exludes rows with missing name data
# - (2) Exludes rows not in washington
# - (3) Exludes rows where 'code' is not 'Induvidual'
def initialFilter(input_path):
    data = pd.read_csv(input_path + ".csv")

    # - (1) Exludes rows with missing name data
    data.dropna(inplace=True, subset=["contributor_name"])

    # - (2) Exludes rows not in washington
    data = data[(data['contributor_state'] == "WA")]

    # - (3) Exludes rows where 'code' is not 'Induvidual'
    data = data[(data['code'] == "Individual")]

    print("data.shape()")
    print(data.shape)

    # Finishes by writing a new csv
    return data

# Read in the data that dedupe accepts 
def readData(input_path):
    data_d = {}
    with open(input_path+".csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = int(row['id'])
            curRow = dict(row)
            curRow = {k: None if not v else v for k, v in curRow.items()}
            data_d[row_id] = curRow

    return data_d

# Uses the dedupe library to find clusters of data (possible duplicates)
def createDupeClusters(input_path):

    data = readData(input_path)

    variables = [
        {"field" : "contributor_address", "type": "String"},
        {"field" : "contributor_name", "type": "String"},
        {"field" : "contributor_city", "type": "String"},
        {"field" : "contributor_state", "type": "String"},
        {"field" : "contributor_zip", "type": "String"}
    ]

    deduper = dedupe.Dedupe(variables)

    training_file = "./Dedupe_Training/political_donations_data"
    if os.path.exists(training_file):
        print('reading labeled examples from ', training_file)
        with open(training_file, 'rb') as f:
            deduper.prepare_training(data, f)
    else:
        deduper.prepare_training(data)

    print('starting active labeling...')
    dedupe.console_label(deduper)
    deduper.train()
    with open (training_file, 'w') as tf:
        deduper.write_training(tf)

    print('clustering...')  
    clustered_dupes = deduper.partition(data, 0.5)
    print('# duplicate sets', len(clustered_dupes))
    cluster_membership = {}
    for cluster_id, (records, scores) in enumerate(clustered_dupes):
        for record_id, score in zip(records, scores):
            cluster_membership[record_id] = {
                "Cluster ID": cluster_id,
                "confidence_score": score
            }

    output_path = input_path+"_clusters"
    with open(output_path+".csv", 'w') as f_output, open(input_path+".csv") as f_input:

        reader = csv.DictReader(f_input)
        fieldnames = ['Cluster ID', 'confidence_score'] + reader.fieldnames

        writer = csv.DictWriter(f_output, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row_id = int(row['id'])
            row.update(cluster_membership[row_id])
            writer.writerow(row)

    return output_path




# Uses clusters from the dedupe library to aggregate donation data
# - Sums the total amount donated
# - Creates a first donated at column
# - Creates a last donated at column
# - Creates a % Republican column (based on donation amount)
# - Creates a % Democrat column (based on donation amount)
def groupByCluster(data):
    print("groupByCluster")
    return data


# Main entry point for the program
def main():

    #curDataPath = "../Data/political_donations_data"
    curDataPath = "../Data/political_donations_data_small"

    curData = initialFilter(curDataPath)
    curDataPath = curDataPath+"_filtered"
    curData.to_csv(path_or_buf=curDataPath+".csv")

    curDataPath = createDupeClusters(curDataPath)

    #curData = groupByCluster(curDataPath)
    #curData.to_csv(path_or_buf=curDataPath+"_aggregated.csv")


if __name__ == "__main__":
   main()