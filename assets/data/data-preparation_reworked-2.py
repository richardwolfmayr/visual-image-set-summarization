# deprecated. was just some experiments

# this script should create the table2-combCite file from main_clean.json and xxxx
# main_clean.json is the export from zotero
# Document Profiles.xlsx is the export from MAXQDA Reports-->Document Profiles
# reworked to create objects and only later write them to the file

# difference to data-preparation_reworked: the higher level categories are also tagged when a lower level category is tagged (at least that was the goal).
# only for category and subcategory, not for subsubcategory and lower. So from MAXQDA it is important that subcategories are tagged, even if the subsubcategories are tagged there

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


# Read in the MAXQDA data
df = pd.read_excel('Document Profiles.xlsx', sheet_name='Sheet1', header=0)

def get_tag_structure():
    tag_structure = []
    last_category = None
    for col in df.columns[3:]:
        pattern = re.compile(r'^(?!\.\.)(.*?)(?: > (.*))?$')
        match = pattern.match(col)
        if match:
            category = match.group(1)
            if match.group(2):
                # if that category has not been stored yet, store it
                # this check is needed, if this category has never been tagged, but only the subcategories. If it has been tagged on its own, it is already stored
                if last_category != category:
                    tag_structure.append({"category": category, "subcategory": "none", "original_col": "column for category created in get_tag_structure()"})
                subcategory = match.group(2)
                # if it comes here, this subcategory has been tagged, but without a subsubcategory
                # if that subcategory has not been stored yet, store it
                tag_structure.append({"category": category, "subcategory": subcategory, "original_col": col})
                last_subcategory = subcategory
            else:
                # it comes here if this category has been tagged without a subcategory. e.g. "Derived Data" without " > Image Features / Visual Features"
                # if that category has not been stored yet, store it
                if last_category != category:
                    tag_structure.append({"category": category, "subcategory": "none", "original_col": col})
                else:
                    print("DOES IT GO HERE?")
            last_category = category
            # ignore the subsubcategories. category is optional, subcategory is mandatory, subsubcategory is optional. This is how it should be tagged in MAXQDA
    return tag_structure


tag_structure = get_tag_structure()
# TODO: there are 49 tags with derived Data in MAXQDA and 51 here.... why?  Probably because of subsubsubcategories... I have to check that

# write into the header.csv file
with open('header.csv', 'w') as f:
    f.write("col_name;img_src;class;category\n")
    # now write the tag structure into the file
    # write one line for each category, one line for each subcategory and one line for each subsubcategory
    category_printed = []
    subcategory_printed = []
    for tag in tag_structure:
        if tag['category'] and tag['subcategory'] == "none" :
            f.write(f"{tag['category']};none;;{tag['category']}\n")
            category_printed.append(tag['category'])
        if tag['subcategory'] != "none":
            f.write(f"{tag['subcategory']};none;;{tag['category']}\n")
            subcategory_printed.append(tag['subcategory'])




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
            # column_name = ' > '.join(filter(None, [tag['category'], tag['subcategory'] if tag['subcategory'] != 'none' else None, tag['subsubcategory'] if tag['subsubcategory'] != 'none' else None]))
            column_name = tag['original_col'] # the original column name
            # TESTING
            # if column_name == "Derived Data > Image Features / Visual Features":
            #     print(f"Tag: {tag}")

            has_tag = column_name in df.columns and row[column_name] != 0 # TODO what happens with the created columns? ==> they are not in the df.columns
            tag_info = {
                'category': tag['category'],
                'subcategory': tag['subcategory'],
                'has_tag': has_tag
            }
            document_info['tags'].append(tag_info)

            # if a subtag is marked with has_tag, the parent tags should also be marked with has_tag
            # e.g. "Derived Data > Image Features / Visual Features" is marked with has_tag, then "Derived Data" should also be marked with has_tag
            if has_tag and tag['subcategory'] != "none":
                # find the parent tag by getting the entry in document_info['tags'] where the category is the same as tag['category']
                # iterate over the tags in the document_info and find the parent tag
                for parent_tag in document_info['tags']:
                    if parent_tag['category'] == tag['category'] and parent_tag['subcategory'] == "none":
                        parent_tag['has_tag'] = True
                        break
        documents_tags.append(document_info)
    return documents_tags

document_tag_list = create_document_tags_list(df, tag_structure)

# Print every tag that the first document has with has_tag == True for testing
# for tag in document_tag_list[0]['tags']:
#     if tag['has_tag']:
#         print(tag)

# works perfectly until here
# for every column where there is a number in the document profiles, the tag information with category, subcategory and subsubcategory is stored in the document_tag_list with has_tag = true,
# for every other it is stored with has_tag = false

# now: print it to table2-combCite.csv

with open('table2-combCite.csv', 'w') as f:
    f.write("Paper#Ref;")
    # get the header from the MAXQDA data with df.columns and iterate over it, skipping the first 3 columns
    # for col in df.columns[3:]:
    #     f.write(f"{col};")
    # f.write("\n")

    category_printed = []
    subcategory_printed = []
    for tag in tag_structure:
        if tag['category'] not in category_printed:
            f.write(f"{tag['category']};")
            category_printed.append(tag['category'])
        if tag['subcategory'] != "none" and tag['subcategory'] not in subcategory_printed:
            f.write(f"{tag['subcategory']};")
            subcategory_printed.append(tag['subcategory'])
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
        f.write(f"{zotero_title}#{item['id']};")
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
            zotero_title = re.sub(r'\W+', '', zotero_title).lower()
            maxqda_title = re.sub(r'\W+', '', maxqda_title).lower()
            # todo: probably more cases like this
            # case insensitive comparison
            if maxqda_title in zotero_title:
                for col in tag_structure:
                    # for every tag in the tag_structure, check if it is set in this document and print 0 or category_number to the file
                    # print(f"Match: {col}")
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
                    else:  # TODO: this should not happen.
                        print(f"ERROR: Category not found: {category}")
                        category_number = 1

                    # for this document find if has_tag is true or false for this tag
                    for tag in document['tags']:
                        if tag['category'] == category and tag['subcategory'] == col['subcategory']:
                            if tag['has_tag']:
                                f.write(f"{category_number};")
                            else:
                                f.write("0;")
                            break




                break



        # for index, row in df.iterrows():
        #     # the row['Document name'] is the closest thing to the title in the zotero data
        #     # it will not be identical though, so I have to find the "most fitting" one
        #     # also, the titles in MAXQDA are cut off, e.g. "Pogorelov et al. - 2017 - ClusterTag Interactive Visualization, Clustering .pdf"
        #     # with regular expression I want to get the part of the title that is in the MAXQDA data
        #     # and compare it to the title in the zotero data
        #     pattern = re.compile(r'.* - \d{4} - (.*)\.pdf')
        #     # now use this pattern to extract the title from the current row
        #     match = pattern.match(row['Document name'])
        #     if match:
        #         maxqda_title = match.group(1)  # group(1) matches the first part of the pattern that is enclosed in brackets ()
        #     else:
        #         print(f"no match for {row['Document name']}")
        #         maxqda_title = row['Document name']
        #
        #     # maxqda titles also do not have any special characters like ":" which is in the zotero titles
        #     # so I have to remove them. I remove any special characters
        #     zotero_title = re.sub(r'\W+', '', zotero_title).lower()
        #     maxqda_title = re.sub(r'\W+', '', maxqda_title).lower()
        #     # todo: probably more cases like this
        #     # case insensitive comparison
        #     if maxqda_title in zotero_title:
        #         for col in df.columns[3:]:
        #             # if the value is not 0, write the number according to class to the file
        #             pattern = re.compile(r'^(?!\.\.)(.*?) > (.*)$')  # there is always a category and a subcategory, but not always a subsubcategory
        #             # now use this pattern to extract the title from the current row
        #             match = pattern.match(col)
        #             if match:
        #                 # print(f"Match: {col}")
        #                 category_number = 1
        #                 category = match.group(1)  # the category. Depending on the category, the class will be different, e.g. 0, 1, 2, 3
        #                 if category == "Input Modalities":
        #                     category_number = 2
        #                 elif category == "Derived Data":
        #                     category_number = 3
        #                 elif category == "Summarization":
        #                     category_number = 4
        #                 elif category == "Summarizing Entities":
        #                     category_number = 5
        #                 elif category == "Visual Layout":
        #                     category_number = 6
        #                 elif category == "Interactions":
        #                     category_number = 7
        #                 elif category == "Tasks":
        #                     category_number = 8
        #                 elif category == "Set size":
        #                     category_number = 9
        #                 elif category == "Application Area":
        #                     category_number = 10
        #                 elif category == "Evaluation":
        #                     category_number = 11
        #                 else:  # TODO: this should not happen
        #                     print(f"Category not found: {category}")
        #                     category_number = 1
        #
        #                 subcategory = match.group(2)  # the actual tag
        #                 # the level 2 , subsubcategory is not needed here
        #             else:
        #                 # TODO: in the level2 or lower, the highest-level-category is not displayed anymore ==> will not be found...
        #                 # e.g. "..> Supplementary Data >  Popularity" instead of "Input Modalities > Supplementary Data >  Popularity"
        #                 print(f"No match: {col}")
        #                 if not display_level_2:
        #                     # skip the printing of the subsubcategory
        #                     continue
        #
        #             # for this row and this column, find which number is in the xlsx file
        #             if row[col] != 0:
        #                 f.write(f"{category_number};")
        #             else:
        #                 f.write("0;")
        #
        #
        #
        #         break
        f.write("\n")
