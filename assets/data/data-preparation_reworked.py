# this script should create the table2-combCite file from main_clean.json and Document Profiles.xlsx
# main_clean.json is the export from zotero
# Document Profiles.xlsx is the export from MAXQDA Reports-->Document Profiles
# It creates objects and only later write them to the file, so in between I can do for example sorting
# unfortunately the Document Profiles.xlsx is not very well-structured, so I have to do some manual work

import json
import re
import pandas as pd

# in order to get e.g. "Input Data" checked, I have to check for "Input Data" and "Input Data > Data Types" and "Input Data > Data Types > Text" etc.
# OR I have to tag "Input Data" by hand if there is a subcategory that is tagged ==> this is the solution I will go for, as the other one brings lots of problems with it (e.g. what if the same subsubcategory name exists in multiple places etc)

# category > tag = category > subcategory... I used different descriptions for the same thing because of different approaches I had


# Load the zotero_data
with open('main_clean.json', 'r') as f:
    zotero_data = json.load(f)

# load only the 20 exploratory papers TODO: change this to the final papers
with open('main_clean_20.json', 'r') as f:
    zotero_data = json.load(f)

# Read in the MAXQDA data
df = pd.read_excel('Document Profiles.xlsx', sheet_name='Sheet1', header=0)

def get_tag_structure():
    tag_structure = []
    for col in df.columns[3:]:
        pattern = re.compile(r'^(?!\.\.)(.*?)(?: > (.*))?$')
        match = pattern.match(col)
        if match:
            category = match.group(1)
            subcategory = match.group(2)
            tag_structure.append({"category": category, "subcategory": subcategory, "original_col": col})
        # if there is a structure like "..> Metadata > Geolocation (+)" it is not matched by the pattern. We do not care about these tags
        # so we have to tag subcategories in MAXQDA by hand, not only the subsubcategories etc
    return tag_structure


tag_structure = get_tag_structure()

# write into the header.csv file
with open('header.csv', 'w') as f:
    f.write("col_name;img_src;class;category\n")
    # now write the tag structure into the file
    for tag in tag_structure:
        # if it has no subcategory, it is only a category-tag ==> don't print this, as we only print the subcategories
        if tag['subcategory'] != "none":
            f.write(f"{tag['subcategory']};none;;{tag['category']}\n")

# the df is a mess ==> create a new structure that is easier to work with
def create_document_tags_list(df, tag_structure):
    documents_tags = []
    for index, row in df.iterrows():
        document_info = {
            'Document group': row['Document group'],
            'Document name': row['Document name'],
            'Document memo': row['Document memo'],
            'tags': []
        }
        for tag in tag_structure:
            # rebuild the column name from the tag structure
            column_name = tag['original_col'] # the original column name
            # TESTING
            # if column_name == "Derived Data > Image Features / Visual Features":
            #     print(f"Tag: {tag}")

            # check if the column exists in the df and if the value is not 0. If it is not 0 in that row, the tag is set
            has_tag = column_name in df.columns and row[column_name] != 0
            tag_info = {
                'category': tag['category'],
                'subcategory': tag['subcategory'],
                'has_tag': has_tag
            }
            document_info['tags'].append(tag_info)
        documents_tags.append(document_info)
    return documents_tags

document_tag_list = create_document_tags_list(df, tag_structure)

# Print every tag that the first document has with has_tag == True for testing

# works perfectly until here
# for every column of structure: "categroy > tag" where there is a number in the document profiles, the tag information with category, subcategory is stored in the document_tag_list with has_tag = true,
# for every other it is stored with has_tag = false
# now: print it to table2-combCite.csv
with open('table2-combCite.csv', 'w') as f:
    f.write("Paper#Ref;")
    for tag in tag_structure:
        # if it has no subcategory, it is only a category-tag ==> don't print this, as we only print the subcategories
        if tag['subcategory'] != "none":
            f.write(f"{tag['subcategory']};")
    f.write("\n")
    #same would work for subsub, but not programmed since I don't want it anyways

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
        # find the corresponding MAXQDA data by iterating over the rows of document_tag_list
        for document in document_tag_list:
            # the row['Document name'] is the closest thing to the title in the zotero data
            # it will not be identical though, so I have to find the "most fitting" one
            # also, the titles in MAXQDA are cut off, e.g. "Pogorelov et al. - 2017 - ClusterTag Interactive Visualization, Clustering .pdf"
            # with regular expression I want to get the part of the title that is in the MAXQDA data
            # and compare it to the title in the zotero data
            pattern = re.compile(r'.* - \d{4} - (.*)')
            # now use this pattern to extract the title from the current row
            match = pattern.match(document['Document name'])
            if match:
                maxqda_title = match.group(1)  # group(1) matches the first part of the pattern that is enclosed in brackets ()
            else:
                print(f"ERROR: no match for {document['Document name']}")
                maxqda_title = document['Document name']

            # maxqda titles also do not have any special characters like ":" which is in the zotero titles
            # so I have to remove them. I remove any special characters
            zotero_title_short = re.sub(r'\W+', '', zotero_title).lower()
            maxqda_title_short = re.sub(r'\W+', '', maxqda_title).lower()
            # todo: probably more cases like this
            # case insensitive comparison
            if maxqda_title_short in zotero_title_short:
                f.write(f"{zotero_title}#{item['id']};") # only print if found (But ALL should be found in the end... just not during the coding, when not all are done)
                for col in tag_structure:
                    # for every tag in the tag_structure, check if it is set in this document and print 0 or category_number to the file
                    # print(f"Match: {col}")
                    # find the category_number to have the correct color in the visualization
                    category_number = 1
                    category = col["category"]  # the category. Depending on the category, the class will be different, e.g. 0, 1, 2, 3
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
                    elif category == "TestGroup1-Category":
                        category_number = 2
                    elif category == "TestGroup2-Category":
                        category_number = 3
                    else:  # TODO: this should not happen
                        print(f"ERROR: Category not found: {category}")
                        category_number = 1

                    for tag in document['tags']: # iterate over all tags in the document (no matter if has tag or not)
                        if tag['category'] == category and tag['subcategory'] == col['subcategory']: # the current tag/subcategory from tag_structure matches the current tag/subcategory in the document
                            if tag['has_tag']:
                                f.write(f"{category_number};")
                            else:
                                f.write("0;")
                            break
                f.write("\n")
                break
