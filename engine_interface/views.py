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
    return render(request=request, template_name="main_interface.html")


@csrf_exempt
def search_index(request):
    query = request.GET.get("query_string")
    opt = request.GET.get("option")

    if not query:
        return HttpResponse(status=400, content="No Query found.")

    exact_query = True
    if opt and opt.lower() == "or":
        exact_query = False

    results = INVERTED_INDEX.search_index(query=query, exact=exact_query)
    print(results)

    if not results or results is None or len(results) == 0:
        return HttpResponse(status=404, content="Sorry:/ No Results Found!")

    file_nos = get_all_file_nos(results)
    if not file_nos or len(file_nos) == 0:
        return HttpResponse(status=404, content="Sorry:/ Cannot get file nos for doc ids!")

    doc_text_results = list()
    for file_no, doc_list in file_nos.items():
        doc_text_results += get_file_docs_text(file_no, doc_list)

    return render(request, "results_display.html", context={"doc_results": doc_text_results})


def get_file_docs_text(file_no, doc_list):
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
            while file_text_idx < len(file_text) and len(doc_id_list) > 0:
                doc_data = file_text[file_text_idx]
                if int(doc_data.get("id")) in doc_list:
                    doc_list_text.append(doc_data)
                    doc_id_list.remove(int(doc_data.get("id")))
                file_text_idx += 1
            return doc_list_text
        return None


def get_all_file_nos(doc_id_list):
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
