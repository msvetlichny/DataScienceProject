countyList = ["Ferry", "Stevens", "Pend", "Oreille", "Lincoln","Spokane", "Adams", "Whitman", "Columbia", "Garfield", "Asotin"]

curDataPath = "../Data/cities_filtered_by_eastern_washinton_county"

import pandas as pd
data = pd.read_csv(curDataPath+".csv")

listToDrop = []
for index, row in data.iterrows():

    countyAccepted = row["County Name"] in countyList

    if(not countyAccepted):
        listToDrop.append(index)

    index += 1

data.drop(listToDrop, inplace=True)

# Make upper case
for index, row in data.iterrows():
    print(row["City Name"].upper())
    data.at[index,"City Name"] = row["City Name"].upper()

curDataPath = curDataPath+"_filtered"
data.to_csv(path_or_buf=curDataPath+".csv")


