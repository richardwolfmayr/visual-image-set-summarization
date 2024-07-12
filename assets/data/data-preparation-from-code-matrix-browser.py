# Works with the MAXQDA24 Code Matrix Browser.xlsx file that is created by MAXQDA

# this script should create the table2-combCite file from main_clean.json and Document Profiles.xlsx
# main_clean.json is the export from zotero
# Document Profiles.xlsx is the export from MAXQDA Reports-->Document Profiles
# It creates objects and only later write them to the file, so in between I can do for example sorting
# unfortunately the Document Profiles.xlsx is not very well-structured, so I have to do some manual work

import json
import re
import pandas as pd

# in order to get e.g. "Data Types" checked, I have to check for "Input Data > Data Types" and "Input Data > Data Types > Text" etc.
# this works well with the code matrix browser, but not with the document profiles
# category > tag ... I used different descriptions for the same thing because of different approaches I had

# reads the MAXQDA24 Code Matrix Browser.xlsx file and the main_clean.json file
# writes into the header.csv file and the table2-combCite.csv file


# Load the zotero_data
with open('main_clean.json', 'r') as f:
    zotero_data = json.load(f)

# load only the 20 exploratory papers TODO: change this to the final papers
with open('main_clean_20.json', 'r') as f:
    zotero_data = json.load(f)

# Read in the MAXQDA data
df = pd.read_excel('MAXQDA24 Code Matrix Browser.xlsx', sheet_name='Sheet1', header=0)


# get all tags and their respective category
# the subtags are not relevant
# examples:
# test_cat_2	... dont care
# test_cat_2 > test_tag_direkt2	... save "test_tag_direkt2" as the tag and "test_cat_2" as the category
# test_cat_2 > test_tag_direkt2 > subtag1 ... dont care
def get_tag_structure():
    tag_structure = []
    for col in df.columns[1:]:
        # pattern = re.compile(r'(.*)\s*>\s*(.*)\s*>?.*') # this is greedy ==> "test_cat_2 > test_tag_direkt2" is capured in group(1) if you use "test_cat_2 > test_tag_direkt2 > subtag1"
        # pattern = re.compile(r'(.*?)\s*>\s*(.*?)\s*>?.*') # this does not capture the tag in group(2)
        pattern = re.compile(r'(.*?)\s*>\s*([^>]+)\s*(?!>).*$')
        match = pattern.match(col)
        if match:
            category = match.group(1)
            tag = match.group(2)
            for tag_entry in tag_structure:
                if tag_entry['category'] == category and tag_entry['tag'] == tag:
                    # the tag already exists, but we have to add another original column name to it
                    # get the tag structure that already exists
                    tag_entry['original_cols'].append(col)
                    break
            else:
                tag_structure.append({"category": category, "tag": tag, "original_cols": [col]})
    return tag_structure


tag_structure = get_tag_structure()

# write into the header.csv file
with open('header.csv', 'w') as f:
    f.write("col_name;img_src;class;category\n")
    # now write the tag structure into the file
    for tag in tag_structure:
        f.write(f"{tag['category']} > {tag['tag']};none;;{tag['category']}\n")


# the df is a mess ==> create a new structure that is easier to work with
def create_document_tags_list(df, tag_structure):
    documents_tags = []
    for index, row in df.iterrows():
        path_and_name = row.iloc[0],  # the first column is the document name and path. It does not have a useful name ==> iloc[0]
        pattern = r'.*\s*>\s*(.*)'  # get the last part of the title, which is the actual document name without the path
        match = re.match(pattern, path_and_name[0])
        document_name = ""
        if match:
            document_name = match.group(1)
        else:
            if path_and_name[0] == "SUM":
                # this is the last row: do nothing
                continue
            else:
                print(f"ERROR: no match for {document_name}")

        document_info = {
            'Document name': document_name,
            'tags': []
        }
        for tag in tag_structure:
            # rebuild the column names from the tag structure
            original_cols = tag['original_cols']  # the original column names

            # get all columns that are in the original_cols list of that tag and check if the current document has any of those columns set to a value != 0
            # this means that the tag is set for this document. If not, the tag is not set for this document
            # e.g. if the document has derived data > graph > distance graph then the tag "graph" is set for this document
            has_tag = False
            for column_name in original_cols:
                if row[column_name] != 0:
                    has_tag = True
                    break
            tag_info = {
                'category': tag['category'],
                'tag': tag['tag'],
                'has_tag': has_tag
            }
            document_info['tags'].append(tag_info)
        documents_tags.append(document_info)
    return documents_tags


document_tag_list = create_document_tags_list(df, tag_structure)

# for every column of the tagstructure: "category > tag" where there is a number in the MAXQDA-file, the tag information with category and tag is stored in the document_tag_list with has_tag = true,
# for every other it is stored with has_tag = false
# now: print it to table2-combCite.csv
with open('table2-combCite.csv', 'w') as f:
    f.write("Paper#Ref;")
    for tag in tag_structure:
        f.write(f"{tag['category']} > {tag['tag']};")
        # IMPORTANT: write the "tag['category']" because otherwise, if we have the same tag word e.g. "none" in multiple categories,
        # it will be overwritten in table.js when reading the data with d3.dsv(';', '../assets/data/table2-combCite.csv')
    f.write("\n")

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
                f.write(f"{zotero_title}#{item['id']};")  # only print if found (But ALL should be found in the end... just not during the coding, when not all are done)
                for col in tag_structure:
                    # for every tag in the tag_structure, check if it is set in this document and print 0 or category_number to the file
                    # print(f"Match: {col}")
                    # find the category_number to have the correct color in the visualization
                    category_number = 0
                    category = col["category"]  # the category. Depending on the category, the class will be different, e.g. 0, 1, 2, 3
                    if category == "Input Modalities":
                        category_number = 1
                    # elif category == "Derived Data":
                    #     category_number = 2
                    elif category == "Image Representation":
                        category_number = 2
                    # elif category == "Summarization":
                    elif category == "Summarization_Design_Factors":
                        category_number = 3
                    elif category == "Summarizing Entities":
                        category_number = 4
                    # elif category == "Visual Layout":
                    elif category == "Spatial Arrangement":
                        category_number = 5
                    # elif category == "Interactions":
                    elif category == "Interactions_Toward_a_Deeper_Understanding":
                        category_number = 6
                    # elif category == "Tasks":
                    elif category == "Goal":
                        category_number = 7
                    elif category == "Set size":
                        category_number = 8
                    elif category == "Evaluation":
                        category_number = 9
                    # elif category == "Application Area":
                    #     category_number = 10
                    # elif category == "test_cat_1":  # ONLY FOR TESTING
                    #     category_number = 1
                    # elif category == "test_cat_2":  # ONLY FOR TESTING
                    #     category_number = 2
                    else:  # TODO: this should not happen
                        print(f"ERROR: Category not found: {category}")
                        category_number = 0

                    for tag in document['tags']:  # iterate over all tags in the document (no matter if has tag or not)
                        if tag['tag'] == None:
                            continue  # skip the category-tags without subcategories
                        if tag['category'] == category and tag['tag'] == col['tag']:  # the current tag from tag_structure matches the current tag in the document
                            if tag['has_tag']:
                                # print(category_number)
                                f.write(f"{category_number};")
                            else:
                                # print(0)
                                f.write("0;")
                            break
                f.write("\n")
                break

# order table2-combCite.csv by has_tag per tag. e.g. every paper that has "metadata" in the category "Input Data" should be first, then every paper that has "text" in the category "Input Data" etc.
# this is important for the visualization, as the order of the categories is important
# The structure of the table2-combCite.csv file is now as follows:
# A summarized photo visualization system with maximal clique finding algorithm#http://zotero.org/groups/3431/items/VUKTFF64;2;0;0;0;0;0;0;0;3;0;0;3;3;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;4;0;0;0;0;0;0;0;0;5;0;0;0;6;0;0;0;0;0;0;0;0;0;0;0;0;0;0;8;0;0;0;0;0;0;0;0;0;0;9;0;0;0;0;0;0;0;0;0;11;0;11;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;
# II-20: Intelligent and pragmatic analytic categorization of image collections#http://zotero.org/groups/3431/items/PRYCUTRS;0;2;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;3;3;0;0;0;3;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;5;0;0;0;6;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;8;0;0;0;8;8;0;8;0;0;0;0;0;0;0;9;0;0;0;11;0;11;0;11;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;
# Similarity-based visualization of large image collections#http://zotero.org/groups/3431/items/FF2IHK9E;0;2;2;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;3;3;0;0;3;0;0;0;0;0;3;3;0;0;0;4;0;0;0;0;4;0;0;0;5;0;0;0;0;0;0;6;0;6;0;0;0;0;0;0;0;0;8;0;0;0;0;0;0;0;0;0;0;0;0;0;9;0;0;0;0;0;0;11;11;0;0;0;0;0;0;0;0;0;7;0;7;0;7;7;0;0;0;0;0;

# Load the CSV data into a pandas DataFrame
file_path = 'table2-combCite.csv'
df = pd.read_csv(file_path, delimiter=';')

# Get all column names except the first one which is Paper#Ref (the title and id of the paper)
sort_columns = df.columns[1:]

# Ensure column names are stripped of any extra spaces
df.columns = df.columns.str.strip()
sort_columns = sort_columns.str.strip()

# Create a sorting key DataFrame by applying a lambda function that returns a tuple of negative values for each row
# print(df.head())
# print(df[sort_columns].head())

# experiments
# df[sort_columns].apply(lambda x: print(x), axis=1) # applies "print" to each row
# df.apply(lambda x: print(x), axis=1) # applies "print" to each row
# df[sort_columns].apply(lambda x: print(-x), axis=1)
# df[sort_columns].apply(lambda x: print(tuple(-x)), axis=1) # https://www.geeksforgeeks.org/python-tuple-function/
# df[sort_columns].apply(lambda x: print(tuple(1 if val != 0 else 0 for val in x)), axis=1) # https://www.geeksforgeeks.org/python-tuple-function/
# my_dict = {'apple': 1, 'banana': 2, 'cherry': 3}
# my_tuple = tuple(my_dict.items())
# my_tuple = tuple(my_dict.values())
# print(my_tuple)

sort_key = df[sort_columns].apply(lambda x: tuple(1 if val != 0 else 0 for val in x), axis=1)
# explanation: df[sort_columns] returns a DataFrame with only the columns that are in sort_columns, so it is just the same but without the first column
# apply() is a method in pandas that applies a function along a specific axis of the DataFrame. https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html. axix=1 means that the function is applied to each row.
# tuple() gets the values like this (1, 0, 0, 0, 1, 0,....)
# I set the value to 1 if it is not 0, otherwise to 0, so I do not have 2s, 3s etc which could interfere with the sorting


# Add the sorting key to the DataFrame
df['sort_key'] = sort_key

# Sort the DataFrame based on the sorting key
# print(df.head())
df_sorted = df.sort_values(by='sort_key',
                           ascending=False)  # works just like sorting strings alphabetically.. the leftmost value is the most important one, then the second one is the second most important etc. Which is what I want.
# print(df_sorted.head())

# Drop the sorting key column
df_sorted = df_sorted.drop(columns=['sort_key'])

# Save the sorted DataFrame back to the same CSV file
df_sorted.to_csv(file_path, index=False, sep=';')
