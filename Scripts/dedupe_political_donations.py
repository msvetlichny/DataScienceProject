"""
program: dedupe_political_donations.py
author: Kostiantyn Makrasnov, Michael Svetlichny, Spencer G
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
def initialFilter(input_path):
    data = pd.read_csv(input_path + ".csv")
    print("Original:")
    print(data.shape)

    # - (1) Exludes rows with missing name data
    data.dropna(inplace=True, subset=["contributor_name"])
    print("1")
    print(data.shape)

    # - (2) Exludes rows where 'code' is not 'Induvidual'
    data = data[(data['code'] == "Individual")]
    print("2")
    print(data.shape)

    # - (3) filters out any state thats not empty or WA
    data2 = data[data["contributor_state"].isna()]
    data = data[data["contributor_state"] == "WA"]
    frames = [data, data2]
    data = pd.concat(frames)
    print("3")
    print(data.shape)
    print("Amount of NA variables")
    print(data2.shape)

    # - (4) filters out entries without atleast address or city info
    data = data[data["contributor_address"].notna() | data["contributor_city"].notna() | data["contributor_zip"].notna()]
    print("4")
    print(data.shape)

    # - (5) Filter out all cities that are in target counties
    filtered_cities = pd.read_csv("../Data/Cities_filtered.csv")
    filtered_cities_list = filtered_cities["City Name"].tolist()
    boolean_series = data.contributor_city.isin(filtered_cities_list)
    data2 = data[data["contributor_city"].isna()]
    data = data[boolean_series] 
    frames = [data, data2]
    data = pd.concat(frames)
    print("5")
    print(data.shape)
    print("Amount of NA variables")
    print(data2.shape)

    # Remnants of a dark past, RIP (just an example)
    # - (6) Exludes rows not in washington (keeps empty cells with addresses )
    # listToDrop = []
    # for index, row in data.iterrows():
    #     if [CONDITION]:
    #         listToDrop.append(index)
    #     if (index % 10000 == 0 and not index == 0):
    #         print(index) 
    #     index += 1

    # print("Got list to drop: length - " + str(len(listToDrop)))
    # print("Dropping rows...")
    # data.drop(listToDrop, inplace=True)
    # print("Done dropping rows...")
    # print("6")
    # print(data.shape)

    # Finishes by writing a new csv
    return data

# Gets all entries from two subsets of political data datasets and removes duplicate entries by combining the id and origin columns
def mergeDataSets(in_path_1, in_path_2):

    data1 = pd.read_csv(in_path_1 + ".csv")
    data2 = pd.read_csv(in_path_2 + ".csv")
    data1["unique_id"] = data1["id"].astype(str) + data1["origin"]
    data2["unique_id"] = data2["id"].astype(str) + data2["origin"]
    dataMerged=pd.concat([data1,data2]).drop_duplicates(subset="unique_id")
    data1Merged=data1.drop_duplicates(subset="unique_id")
    data2Merged=data2.drop_duplicates(subset="unique_id")

    print("Original Sizes:")
    print(data1.shape)
    print(data2.shape)
    print("Intraset Duplicates Removed:")
    print(data1Merged.shape)
    print(data2Merged.shape)
    print("Combined Set Duplicates Removed:")
    print(dataMerged.shape)
    return dataMerged

# Read in the data that dedupe accepts 
def readData(input_path):
    data_d = {}
    with open(input_path+".csv", encoding="utf8") as f:
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

    # Base name for data set (don't change)
    curDataPath = "../Data/political_donations_data"

    # #STEP 1: Filter the data (then comment out)
    # curData = initialFilter(curDataPath)
    # curDataPath = curDataPath+"_filtered"
    # curData.to_csv(path_or_buf=curDataPath+".csv")

    #STEP 2: Merge data with any other data sets (id and origin fields together make rows unique) (then comment out)
    # curDataPath1 = "../Data/political_donations_data_filtered_python"
    # curDataPath2 = "../Data/political_donations_data_filtered_r"
    # curData = mergeDataSets(curDataPath1, curDataPath2)
    # curDataPath =  curDataPath+"_merged"
    # curData.to_csv(path_or_buf=curDataPath+".csv")

    #STEP 3: Create dupelicate cluster (then comment out)
    curDataPath = curDataPath+"_merged"
    curDataPath = createDupeClusters(curDataPath)

    # #STEP 4: Aggregate the clusters
    #curData = groupByCluster(curDataPath)
    #curData.to_csv(path_or_buf=curDataPath+"_aggregated.csv")


if __name__ == "__main__":
   main()