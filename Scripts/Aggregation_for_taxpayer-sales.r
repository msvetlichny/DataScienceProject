#############################
# Author(s): Michael S., Kostia M., Spencer G.
# Date: 5/7/2021
# Objective: Create one central Spokane City dataframe
# Source: https://gisdatacatalog-spokanecounty.opendata.arcgis.com/pages/treasurer-data
#############################

install.packages("rstudioapi")
install.packages("plyr")
install.packages("dplyr")
install.packages("hrbrthemes")


library(plyr)
library(dplyr)

library(hrbrthemes)

#This sets the working directory to the folder 
setwd(dirname(rstudioapi::getSourceEditorContext()$path))

#Read in our CSV files
data           <- read.csv("spokane_house_sales_filtered_clusters_cleaned.csv")
pol_data       <- read.csv("political_donations_data.csv")


# Code to combine taxpayer & sales dataframes
############################################################
# NOTE: May have to use "ï..parcel" or "parcel" depending on how R reads in the .csv files
taxpayer_data  <- read.csv("taxpayer_info.csv")
sales_data     <- read.csv("sales_info.csv")
combined_taxpayer_sales <- dplyr::full_join(taxpayer_data, sales_data, by = "ï..parcel")

############################################################


#Below code is for "data"
############################################################
# algorithm may take a few minutes to run
# Below function from the "plyr" package seeks to sum all "gross_sale_price" 
# values holding the defined variables as unique identifiers. In other words, 
# "gross_sale_price" will only get summed if "Cluster.ID", "confidence_score",
# etc., are all the same for the series of records.
data3 <- ddply(data,.(Cluster.ID, confidence_score, taxpayer, 
                      address_1, city, state, zip), summarize, 
               sum=sum(gross_sale_price),number=length(Cluster.ID))


# Remove all T-mobile entries and their cell towers
#data4 <- data3[!apply(data3$taxpayer == "4 MOBILE",1,all), ]

data4 <- data3[!grepl(c("MOBILE"), data3$taxpayer),]
dataFun <- data4[!grepl(c("LLC"), data4$taxpayer),]


############################################################


# Below code is for "pol_data"
############################################################


# Store all zipcodes found in counties that Innovia listed
zip <- c(99208,99205,99206,99223,99207,99216,99224,99203,99004,99212,99202,99201,99217,99016,99037,99218,99006,99019,99156,99021,99026,99204,99005,99022,99001,99027,99003,99025,99009,99011,99228,99209,99214,99036,99029,99031,99013,99170,99220,99030,99210,99033,99012,99219,99213,99023,99211,99018,99014,99215,99020,99039,99015,99251,99252,99256,99258,99260,99299,99403,99402,99401,99166,99138,99118,99121,99150,99140,99160,99107,99114,99141,99109,99148,99181,99173,99110,99101,99157,99040,99167,99126,99129,99137,99146,99034,99151,99131,99169,99159,99032,99341,99327,99332,99139,99119,99180,99153,99152,99122,99185,99134,99008,99117,99147,99144,99154,99163,99111,99161,99171,99130,99113,99143,99125,99158,99102,99179,99128,99149,99176,99017,99105,99333,99136,99174,99104,99127,99164,99165,99328,99347,99359,99347)

# Create a new dataframe from political_donations_data.csv filtering our zipcodes
pol_data_select <- pol_data[pol_data$contributor_zip %in% zip,]

# Filter just retired people
retired <- c("RETIRED", "Retired", "retired")
pol_data_select_retired <- pol_data_select[pol_data_select$contributor_occupation %in% retired,]

# Filter >=$500, Retired, and in all the specified zip codes
pol_data_select_retired_500 <- pol_data_select_retired[pol_data_select_retired$amount >= 500, ]
write.csv(pol_data_select_retired_500, "High_priority_target_donors.csv")

#Output useful CSV files
write.csv(pol_data_select, "Filtered_pol_data.csv")
write.csv(pol_data_select_retired_500, "Filtered_pol_data_retired_500.csv")

# AGGREGATE DATA - algorithm may take a few minutes to run
pol_data_agg <- ddply(pol_data_select,.(contributor_name, contributor_address, contributor_city, contributor_state), summarize, 
               sum=sum(amount),number=length(contributor_name))


############################################################


# Code to combine datasets
############################################################
tax_data_agg <- data4
tax_data_agg$contributor_name <- tax_data_agg$taxpayer

combined_taxpayer_pol <- dplyr::full_join(tax_data_agg, pol_data_agg, by = "contributor_name")

# Rename columns to make sense
combined_taxpayer_pol <- combined_taxpayer_pol %>%
  rename(
    gross_sale_price          = sum.x,
    total_properties          = number.x, 
    total_contributions       = sum.y, 
    total_amount_of_donations = number.y 
  )

#Omit the NA's
combined_taxpayer_pol1 <- combined_taxpayer_pol[complete.cases(combined_taxpayer_pol$taxpayer),]
combined_taxpayer_pol2 <- combined_taxpayer_pol1[complete.cases(combined_taxpayer_pol1$contributor_address),]

combined_taxpayer_pol3 <- combined_taxpayer_pol2[!grepl(c("AVISTA"), combined_taxpayer_pol2$taxpayer),]
analysis_set <- combined_taxpayer_pol3[complete.cases(combined_taxpayer_pol3$gross_sale_price),]

analysis_set$contributor_city[analysis_set$contributor_city ==" SPOKANE"] <- "SPOKANE"
analysis_set$contributor_city[analysis_set$contributor_city =="  SPOKANE"] <- "SPOKANE"
analysis_set$contributor_city[analysis_set$contributor_city =="Spokane"] <- "SPOKANE"

analysis_set$city[analysis_set$city ==" SPOKANE"] <- "SPOKANE"
analysis_set$city[analysis_set$city =="  SPOKANE"] <- "SPOKANE"
analysis_set$city[analysis_set$city =="Spokane"] <- "SPOKANE"

#Omit AVISTA
write.csv(combined_taxpayer_pol3, "Combined_taxpayer_and_political_contributions.csv")

#Perform an analysis
############################################################

#linear_model1 <- lm(gross_sale_price ~ total_properties + total_contributions + total_amount_of_contributions, analysis_set)
#summary(linear_model1)

#linear_model2 <- lm(gross_sale_price ~ total_properties + total_contributions, analysis_set)
#summary(linear_model2)
#No significant information found

############################################################




# OTHER - SCRAP 
############################################################
############################################################
############################################################

#Remove empty records from the data (rows with no data)
#data[apply(data == "",1,all), ]

# pol_data1 <- pol_data[(pol_data$contributor_state == "WA" | pol_data$contributor_state == "") & 
#                         (pol_data$contributor_city != "" | pol_data$contributor_address != ""), ]
# pol_data2 <- pol_data1[(pol_data1$contributor_city != "SEATTLE"),]
# pol_data3 <- pol_data2[(pol_data2$contributor_city != "OLYMPIA"),]
# pol_data4 <- pol_data[(pol_data$contributor_city %in% c("HATTON" ,"LIND" ,"OTHELLO" ,"RITZVILLE" ,"WASHTUCNA" ,"ASOTIN" ,"CLARKSTON" ,"CLARKSTON" ,"DAYTON" ,"STARBUCK" ,"BARNEYS JUNCTION" ,"BARSTOW" ,"BOYDS" ,"CURLEW" ,"CURLEW LAKE" ,"DANVILLE" ,"INCHELIUM" ,"KELLER" ,"LAURIER" ,"MALO" ,"ORIENT" ,"PINE GROVE" ,"REPUBLIC" ,"TORBOY" ,"TWIN LAKES" ,"POMEROY" ,"ALMIRA" ,"CRESTON" ,"DAVENPORT" ,"HARRINGTON" ,"ODESSA" ,"REARDAN" ,"SPRAGUE" ,"WILBUR" ,"CUSICK" ,"IONE" ,"METALINE" ,"METALINE FALLS" ,"NEWPORT" ,"AIRWAY HEIGHTS" ,"CHENEY" ,"COUNTRY HOMES" ,"DEER PARK" ,"FAIRCHILD AFB" ,"FAIRFIELD" ,"FAIRWOOD" ,"FOUR LAKES" ,"GREEN BLUFF" ,"LATAH" ,"LIBERTY LAKE" ,"MEAD" ,"MEDICAL LAKE" ,"MILLWOOD" ,"OTIS ORCHARDS" ,"ROCKFORD" ,"SPANGLE" ,"SPOKANE" ,"SPOKANE VALLEY" ,"TOWN AND COUNTRY" ,"WAVERLY" ,"ADDY" ,"CHEWELAH" ,"CLAYTON" ,"COLVILLE" ,"KETTLE FALLS" ,"LOON LAKE" ,"MARCUS" ,"NORTHPORT" ,"SPRINGDALE" ,"VALLEY" ,"ALBION" ,"COLFAX" ,"COLTON" ,"ENDICOTT" ,"FARMINGTON" ,"GARFIELD" ,"LACROSSE" ,"LAMONT" ,"MALDEN" ,"OAKESDALE" ,"PALOUSE" ,"PULLMAN" ,"ROSALIA" ,"ST. JOHN" ,"STEPTOE" ,"TEKOA" ,"UNIONTOWN")),]

#ggplot(analysis_set, aes(x = contributor_city)) +
#  ggtitle("Average Property Values and Donation by City in Eastern WA") +
#  geom_bar(aes(fill = city), position = "fill") +
#  theme(plot.title = element_text(hjust = 0.5))

#data_test <- data.frame(
#  type = c( rep("Gross Sale Price",506), rep("Total Contributions",506) ),
#  value = c( analysis_set$gross_sale_price, analysis_set$total_contributions )
#)


#p <- data_test %>%
#  ggplot( aes(x=value, fill=type)) +
#  geom_histogram( color="#e9ecef", alpha=0.6, position = 'identity') +
#  scale_fill_manual(values=c("#69b3a2", "#404080")) +
#  theme_ipsum() +
#  labs(fill="")
#plot(p)



