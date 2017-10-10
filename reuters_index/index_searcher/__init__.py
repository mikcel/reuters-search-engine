import nltk
import pickle

from ..reuters_parser import Parser


class IndexSearcher:
    def __init__(self, inverted_index_path):
        self.inverted_index_path = inverted_index_path
        self.inverted_index = None
        self.open_index()

    def open_index(self):

        try:
            with open(self.inverted_index_path, "rb") as file_obj:
                self.inverted_index = pickle.load(file_obj)
        except (OSError, IOError):
            print("Error Open index")

    def search_index(self, query, exact=True):

        if query is None or query == "":
            print("Enter a correct query!")
            return False

        keywords = nltk.word_tokenize(query)

        keywords_processed = Parser.preprocess_tokens(tokens=keywords, downcase=True, no_digits=True, rule_of_thirty=True,
                                                      stop_words_150=True, stemming=False)

        if keywords_processed is None or len(keywords_processed) == 0 and all([not keyword.isalpha() for keyword in keywords_processed]):
            print("No words found in query. Stop words are removed!")
            return False

        keywords_postings = list()
        for keyword in keywords_processed:
            if keyword in self.inverted_index:
                keywords_postings.append(self.inverted_index[keyword])
            elif exact:
                print("One keyword in the query was not found in the index: %s" % keyword)
                return None

        keywords_postings = sorted(keywords_postings, key=lambda p_list: len(p_list))

        iter_postings = iter(keywords_postings)
        docs_id_matched = next(iter_postings)

        for postings in iter_postings:
            if exact:
                docs_id_matched = self.intersect_and(docs_id_matched, postings)
            else:
                docs_id_matched = self.intersect_or(docs_id_matched, postings)

        return docs_id_matched

    def intersect_and(self, first_list, second_list):

        iter_first_list = iter(first_list)
        iter_scnd_list = iter(second_list)

        first_list_post = next(iter_first_list, None)
        scnd_list_post = next(iter_scnd_list, None)

        matched_items = list()
        while first_list_post is not None and scnd_list_post is not None:

            if first_list_post == scnd_list_post:
                matched_items.append(first_list_post)
                first_list_post = next(iter_first_list, None)
                scnd_list_post = next(iter_scnd_list, None)

            elif first_list_post < scnd_list_post:
                first_list_post = next(iter_first_list, None)

            else:
                scnd_list_post = next(iter_scnd_list, None)

        return matched_items

    def intersect_or(self, first_list, second_list):

        combined_list = sorted(first_list + second_list)
        return set(combined_list)
