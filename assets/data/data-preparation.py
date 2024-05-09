# this script should create the table2-combCite file from main_clean.json and xxxx
# main_clean.json is the export from zotero
# xxx is the export from MAXQDA

import json
import re
import pandas as pd

# Load the zotero_data
with open('main_clean.json', 'r') as f:
    zotero_data = json.load(f)

# Write into the table2-combCite.csv file
# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref,Adaptive Systems,Evaluation of Systems and Algorithms,Model Steering and Active Learning,Replication,Report Generation,Understanding the User,Grammar,Graph,Model,Sequence,Classification Models,Pattern Analysis,Probabilistic Models/Prediction,Program Synthesis,Interactive Visual Analysis\n")
#     for item in zotero_data:
#         f.write(f"{item['title']}#{item['id']},0,1,1,0,0,1,1,0,0,2,2,3,3,0,0\n") # todo add the actual codings


# THIS ONE worked
# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref;Adaptive Systems;Evaluation of Systems and Algorithms;Model Steering and Active Learning;Replication;Report Generation;Understanding the User;Grammar;Graph;Model;Sequence;Classification Models;Pattern Analysis;Probabilistic Models/Prediction;Program Synthesis;Interactive Visual Analysis\n")
#     for item in zotero_data:
#         # manually fix two titles:
#         # Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales; [Design di interfacce avanzato per IIIF. Uno strumento digitale per esplorare collezioni di immagini a diverse scale]
#         # remove the spanish title
#         if item['title'] == "Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales; [Design di interfacce avanzato per IIIF. Uno strumento digitale per esplorare collezioni di immagini a diverse scale]":
#             item['title'] = "Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales"
#
#         # "Picture the scene⋯" visually summarising social media events
#         # fix the dots
#         if item['title'] == "\"Picture the scene⋯\" visually summarising social media events":
#             item['title'] = "\'Picture the scene...\' visually summarising social media events"
#
#         f.write(f"{item['title']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n") # todo add the actual codings

# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref;Adaptive Systems;Evaluation of Systems and Algorithms;Model Steering and Active Learning;Replication;Report Generation;Understanding the User;Grammar;Graph;Model;Sequence;Classification Models;Pattern Analysis;Probabilistic Models/Prediction;Program Synthesis;Interactive Visual Analysis\n")
#     for item in data:
#         f.write(f"{item['author'][0]['family']} et al {item['issued']['date-parts']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n") # todo add the actual codings

# Read in the MAXQDA data

df = pd.read_excel('Document Profiles.xlsx', sheet_name='Sheet1', header=0)

# write into the header.csv file
with open('header.csv', 'w') as f:
    f.write("col_name;img_src;class;category\n")
    # get the header from the MAXQDA data with df.columns and iterate over it, skipping the first 3 columns
    for col in df.columns[3:]:
        f.write(f"{col};none;;\n")
    f.write("\n")


with open('table2-combCite.csv', 'w') as f:
    f.write("Paper#Ref;")
    # get the header from the MAXQDA data with df.columns and iterate over it, skipping the first 3 columns
    for col in df.columns[3:]:
        f.write(f"{col};")
    f.write("\n")

    # f.write("Paper#Ref;Adaptive Systems;Evaluation of Systems and Algorithms;Model Steering and Active Learning;Replication;Report Generation;Understanding the User;Grammar;Graph;Model;Sequence;Classification Models;Pattern Analysis;Probabilistic Models/Prediction;Program Synthesis;Interactive Visual Analysis\n")
    for item in zotero_data:
        # manually fix two titles:
        # Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales; [Design di interfacce avanzato per IIIF. Uno strumento digitale per esplorare collezioni di immagini a diverse scale]
        # remove the spanish title
        if item[
            'title'] == "Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales; [Design di interfacce avanzato per IIIF. Uno strumento digitale per esplorare collezioni di immagini a diverse scale]":
            item['title'] = "Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales"

        # "Picture the scene⋯" visually summarising social media events
        # fix the dots
        if item['title'] == "\"Picture the scene⋯\" visually summarising social media events":
            item['title'] = "\'Picture the scene...\' visually summarising social media events"

        # f.write(f"{item['title']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n")
        # todo add the actual codings

        zotero_title = item['title']
        f.write(f"{zotero_title}#{item['id']};")
        # find the corresponding MAXQDA data
        for index, row in df.iterrows():
            # the row['Document name'] is the closest thing to the title in the zotero data
            # it will not be identical though, so I have to find the "most fitting" one
            # also, the titles in MAXQDA are cut off, e.g. "Pogorelov et al. - 2017 - ClusterTag Interactive Visualization, Clustering .pdf"
            # with regular expression I want to get the part of the title that is in the MAXQDA data
            # and compare it to the title in the zotero data
            pattern = re.compile(r'.* - \d{4} - (.*)\.pdf')
            # now use this pattern to extract the title from the current row
            match = pattern.match(row['Document name'])
            if match:
                maxqda_title = match.group(1) # group(1) matches the first part of the pattern that is enclosed in brackets ()
            else:
                print(f"no match for {row['Document name']}")
                maxqda_title = row['Document name']

            # maxqda titles also do not have any special characters like ":" which is in the zotero titles
            # so I have to remove them. I remove any special characters
            zotero_title = re.sub(r'\W+', '', zotero_title).lower()
            maxqda_title = re.sub(r'\W+', '', maxqda_title).lower()
            # todo: probably more cases like this
            # case insensitive comparison
            if maxqda_title in zotero_title:
                for col in df.columns[3:]:
                    f.write(f"{row[col]};")
                break
        f.write("\n")


