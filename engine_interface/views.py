"""
Views.py
Contains methods to handle HTTP requests for the app
"""
import json
import os
from search_engine.settings import BASE_DIR
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from reuters_index.index_searcher import IndexSearcher
from reuters_index.reuters_parser import Parser

# Define path to the directories/files of parsed collection
REUTERS_DIR_PATH = os.path.join(BASE_DIR, "reuters_index")
COLLECTION_PATH = os.path.join(REUTERS_DIR_PATH, "reuters_parser", "reuters-data")
INVERTED_INDEX_PATH = os.path.join(REUTERS_DIR_PATH, "parsed_data", "inverted_index.bin")

INVERTED_INDEX = IndexSearcher(INVERTED_INDEX_PATH)


def index(request):
    """
    Function to load the search engine page
    :param request: Request object
    :return: Rendered template
    """
    return render(request=request, template_name="main_interface.html")


@csrf_exempt
def search_index(request):
    """
    Method to search the inverted index given a query and the option for querying (AND and OR)
    :param request: Request object
    :return: HTTP response with error code if error, otherwise rendered template containing docs retrieved
    """

    # Fetch query parameters
    query = request.GET.get("query_string")
    opt = request.GET.get("option")

    # Check query presence
    if not query:
        return HttpResponse(status=400, content="No Query found.")

    # Check for AND or OR
    exact_query = True
    if opt and opt.lower() == "or":
        exact_query = False

    # Get results (doc_ids) from searcher
    results = INVERTED_INDEX.search_index(query=query, exact=exact_query)

    # Check that results were found
    if not results or results is None or len(results) == 0:
        return HttpResponse(status=404, content="Sorry :/ No Results Found!")

    # Fetch all the file nos to be read
    file_nos = get_all_file_nos(results)
    if not file_nos or len(file_nos) == 0:
        return HttpResponse(status=404, content="Sorry :/ Cannot get file nos for doc ids!")

    # Get the text for each document in a file
    doc_text_results = list()
    for file_no, doc_list in file_nos.items():
        doc_text_results += get_file_docs_text(file_no, doc_list)

    return render(request, "results_display.html", context={"doc_results": doc_text_results})


def get_all_file_nos(doc_id_list):
    """
    Method to retrieve all file nos of the docs in list passed
    :param doc_id_list: List of doc ids to retrieve file no
    :return: dict with file no and list of doc id in this file
    """
    try:
        with open(os.path.join(COLLECTION_PATH, "doc_id_file_mapping.json"), "r") as mapping_file:
            doc_map = json.load(mapping_file)
    except (OSError, IOError):
        return None
    else:
        doc_id_file_no = dict()
        # Get the file mapping for each doc
        for mapping in doc_map:
            range_doc = mapping.get("range")
            for doc_id in doc_id_list:
                if range_doc[0] < doc_id < range_doc[len(range_doc) - 1]:
                    file_no = mapping.get("file_no")
                    if file_no in doc_id_file_no:
                        doc_id_file_no[file_no] += [doc_id]
                    else:
                        doc_id_file_no[file_no] = [doc_id]
        return doc_id_file_no


def get_file_docs_text(file_no, doc_list):
    """
    Helper method to retrieve the docs text based on the file no obtained
    :param file_no: the corresponding file no to retrieved docs in list passed
    :param doc_list: list of docs to retrieve in the file with the corresponding file no passed
    :return: list of docs with all text needed
    """
    try:
        with open(os.path.join(COLLECTION_PATH, "reut2-%03d.sgm" % file_no), "rb") as reuters_file:
            file_text = Parser().parse_file(reuters_file.read(), preprocess=False)
    except (OSError, IOError):
        return None
    else:
        if file_text:
            doc_list_text = list()
            doc_id_list = doc_list
            file_text_idx = 0

            """ Check the file parsed and the docs that pertain to this file - doesn't continue if all docs 
            were fetched"""
            while file_text_idx < len(file_text) and len(doc_id_list) > 0:
                doc_data = file_text[file_text_idx]
                if int(doc_data.get("id")) in doc_list:
                    doc_list_text.append(doc_data)
                    doc_id_list.remove(int(doc_data.get("id")))
                file_text_idx += 1
            return doc_list_text
        return None


