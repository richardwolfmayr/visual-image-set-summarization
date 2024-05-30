# this script should create the table2-combCite file from main_clean.json and xxxx
# main_clean.json is the export from zotero
# Document Profiles.xlsx is the export from MAXQDA Reports-->Document Profiles

import json
import re
import pandas as pd

# settings: e.g. if the level 2 tags should be displayed: (level 0 = category, level 1 = subcategory, level 2 = subsubcategory)
display_level_2 = False # TODO: actually I would need the same system as for the categories (print the category only once ---> print the subcategory only once when there are multiple subsubcategories)

# TODO: in order to get e.g. "Input Data" checked, I have to check for "Input Data" and "Input Data > Data Types" and "Input Data > Data Types > Text" etc.
# OR I have to tag "Input Data" by hand if there is a subcategory that is tagged


# Load the zotero_data
with open('main_clean.json', 'r') as f:
    zotero_data = json.load(f)

# load only the 20 exploratory papers
with open('main_clean_20.json', 'r') as f:
    zotero_data = json.load(f)

# Write into the table2-combCite.csv file
# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref,Adaptive Systems,Evaluation of Systems and Algorithms,Model Steering and Active Learning,Replication,Report Generation,Understanding the User,Grammar,Graph,Model,Sequence,Classification Models,Pattern Analysis,Probabilistic Models/Prediction,Program Synthesis,Interactive Visual Analysis\n")
#     for item in zotero_data:
#         f.write(f"{item['title']}#{item['id']},0,1,1,0,0,1,1,0,0,2,2,3,3,0,0\n") #


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
#         f.write(f"{item['title']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n") #

# with open('table2-combCite.csv', 'w') as f:
#     f.write("Paper#Ref;Adaptive Systems;Evaluation of Systems and Algorithms;Model Steering and Active Learning;Replication;Report Generation;Understanding the User;Grammar;Graph;Model;Sequence;Classification Models;Pattern Analysis;Probabilistic Models/Prediction;Program Synthesis;Interactive Visual Analysis\n")
#     for item in data:
#         f.write(f"{item['author'][0]['family']} et al {item['issued']['date-parts']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n") # todo add the actual codings

# Read in the MAXQDA data

df = pd.read_excel('Document Profiles.xlsx', sheet_name='Sheet1', header=0)


# create a function for going over the header data from Document Profiles.xlsx
# get the header from the MAXQDA data with df.columns and iterate over it, skipping the first 3 columns
def write_header_from_maxqda(f, for_table2=False):
    printed_categories = []
    for col in df.columns[3:]:
        if display_level_2:
            if for_table2:
                f.write(f"{col};")
            else:
                f.write(f"{col};none;;\n")
        else:
            # pattern = re.compile(r'^(?!\.\.)(.*?) > (.*)$')  # there is always a category and a subcategory, but not always a subsubcategory
            pattern = re.compile(r'^(?!\.\.)(.*?)(?: > (.*))?$')  # this allows for no subcategory (e.g. "Input Modalities")
            # now use this pattern to extract the title from the current row
            match = pattern.match(col)
            if match:
                # first: check if the category is already printed
                category = match.group(1)
                if category not in printed_categories:
                    printed_categories.append(category)
                    if for_table2:
                        f.write(f"{category};")
                    else:
                        f.write(f"{category};none;;\n")
                if match.group(2):
                    if for_table2:
                        f.write(f"{match.group(2)};")
                    else:
                        f.write(f"{match.group(2)};none;;\n")  # print the subcategory
            else:
                # do nothing
                print(f"No match: {col}")
    f.write("\n")


# write into the header.csv file
with open('header.csv', 'w') as f:
    f.write("col_name;img_src;class;category\n")
    # get the header from the MAXQDA data with df.columns and iterate over it, skipping the first 3 columns
    write_header_from_maxqda(f)

with open('table2-combCite.csv', 'w') as f:
    f.write("Paper#Ref;")
    # get the header from the MAXQDA data with df.columns and iterate over it, skipping the first 3 columns
    # for col in df.columns[3:]:
    #     f.write(f"{col};")
    # f.write("\n")

    write_header_from_maxqda(f, True)

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

        # testcoding: f.write(f"{item['title']}#{item['id']};0;1;1;0;0;1;1;0;0;2;2;3;3;0;0\n")
        # add the actual codings
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
                maxqda_title = match.group(1)  # group(1) matches the first part of the pattern that is enclosed in brackets ()
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
                    # if the value is not 0, write the number according to class to the file
                    pattern = re.compile(r'^(?!\.\.)(.*?) > (.*)$')  # there is always a category and a subcategory, but not always a subsubcategory
                    # now use this pattern to extract the title from the current row
                    match = pattern.match(col)
                    if match:
                        # print(f"Match: {col}")
                        category_number = 1
                        category = match.group(1)  # the category. Depending on the category, the class will be different, e.g. 0, 1, 2, 3
                        if category == "Input Modalities":
                            category_number = 2
                        elif category == "Derived Data":
                            category_number = 3
                        elif category == "Summarization":
                            category_number = 4
                        elif category == "Summarizing Entities":
                            category_number = 5
                        elif category == "Visual Layout":
                            category_number = 6
                        elif category == "Interactions":
                            category_number = 7
                        elif category == "Tasks":
                            category_number = 8
                        elif category == "Set size":
                            category_number = 9
                        elif category == "Application Area":
                            category_number = 10
                        elif category == "Evaluation":
                            category_number = 11
                        else:  # TODO: this should not happen
                            print(f"Category not found: {category}")
                            category_number = 1

                        subcategory = match.group(2)  # the actual tag
                        # the level 2 , subsubcategory is not needed here
                    else:
                        # TODO: in the level2 or lower, the highest-level-category is not displayed anymore ==> will not be found...
                        # e.g. "..> Supplementary Data >  Popularity" instead of "Input Modalities > Supplementary Data >  Popularity"
                        print(f"No match: {col}")
                        if not display_level_2:
                            # skip the printing of the subsubcategory
                            continue

                    # for this row and this column, find which number is in the xlsx file
                    if row[col] != 0:
                        f.write(f"{category_number};")
                    else:
                        f.write("0;")



                break
        f.write("\n")
