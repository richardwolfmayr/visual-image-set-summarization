# this script should create the table2-combCite file from main_clean.json and xxxx
# main_clean.json is the export from zotero
# xxx is the export from MAXQDA

import json

# Load the data
with open('main_clean.json', 'r') as f:
    data = json.load(f)

# Write into the table2-combCite.csv file
# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref,Adaptive Systems,Evaluation of Systems and Algorithms,Model Steering and Active Learning,Replication,Report Generation,Understanding the User,Grammar,Graph,Model,Sequence,Classification Models,Pattern Analysis,Probabilistic Models/Prediction,Program Synthesis,Interactive Visual Analysis\n")
#     for item in data:
#         f.write(f"{item['title']}#{item['id']},0,1,1,0,0,1,1,0,0,2,2,3,3,0,0\n") # todo add the actual codings


with open('table2-combCite.csv', 'w') as f:
    f.write("Paper#Ref;Adaptive Systems;Evaluation of Systems and Algorithms;Model Steering and Active Learning;Replication;Report Generation;Understanding the User;Grammar;Graph;Model;Sequence;Classification Models;Pattern Analysis;Probabilistic Models/Prediction;Program Synthesis;Interactive Visual Analysis\n")
    for item in data:
        # manually fix two titles:
        # Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales; [Design di interfacce avanzato per IIIF. Uno strumento digitale per esplorare collezioni di immagini a diverse scale]
        # remove the spanish title
        if item['title'] == "Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales; [Design di interfacce avanzato per IIIF. Uno strumento digitale per esplorare collezioni di immagini a diverse scale]":
            item['title'] = "Advanced Interface Design for IIIF A Digital Tool to Explore Image Collections at Different Scales"

        # "Picture the scene⋯" visually summarising social media events
        # fix the dots
        if item['title'] == "\"Picture the scene⋯\" visually summarising social media events":
            item['title'] = "\'Picture the scene...\' visually summarising social media events"

        f.write(f"{item['title']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n") # todo add the actual codings


# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref;Adaptive Systems;Evaluation of Systems and Algorithms;Model Steering and Active Learning;Replication;Report Generation;Understanding the User;Grammar;Graph;Model;Sequence;Classification Models;Pattern Analysis;Probabilistic Models/Prediction;Program Synthesis;Interactive Visual Analysis\n")
#     for item in data:
#         f.write(f"{item['author'][0]['family']} et al {item['issued']['date-parts']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n") # todo add the actual codings
