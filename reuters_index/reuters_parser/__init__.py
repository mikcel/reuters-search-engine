import json
import re
import os
from bs4 import BeautifulSoup
from nltk import tokenize
from nltk.corpus import stopwords
from reuters_parser.porter_stemmer import PorterStemmer

STOP_WORDS_30 = ["the", "of", "to", "and", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are",
                 "with", "as", "I", "his", "they", "be", "at", "one", "have", "this", "from", "or", "had", "by", "hot"]

STOP_WORDS_30_MORE = STOP_WORDS_30 + ["but", "some", "what", "there", "we", "can", "out", "other", "were", "all",
                                      "your", "when", "up",
                                      "use", "word", "how", "said", "an", "each", "she", "which", "do", "their", "time",
                                      "if", "will",
                                      "way", "about", "many", "then", "them", "would", "write", "like", "so", "these",
                                      "her", "long",
                                      "make", "thing", "see", "him", "two", "has", "look", "more", "day", "could", "go",
                                      "come", "did",
                                      "my", "sound", "no", "most", "number", "who", "over", "know", "water", "than",
                                      "call", "first",
                                      "people", "may", "down", "side", "been", "now", "find", "any", "new", "work",
                                      "part", "take", "get",
                                      "place", "made", "live", "where", "after", "back", "little", "only", "round",
                                      "man", "year", "came",
                                      "show", "every", "good", "me", "give", "our", "under", "name", "very", "through",
                                      "just", "form",
                                      "much", "great", "think", "say", "help", "low", "line", "before", "turn", "cause",
                                      "same", "mean",
                                      "differ", "move", "right", "boy", "old", "too", "does", "tell"]


class Parser:
    def parse_file(self, file_text="", process_settings=None):
        parsed_docs = self.parse_documents(file_text=file_text)

        return self.tokenize_docs(parsed_docs, process_settings)

    def parse_documents(self, file_text):

        parsed_text = BeautifulSoup(file_text, "html.parser")

        docs = []
        for doc in parsed_text.find_all("reuters"):

            doc_info = {}
            if doc.attrs.get("newid"):
                doc_info["id"] = doc.attrs.get("newid")
            else:
                continue

            doc_text = doc.find(re.compile("^text$", re.IGNORECASE))
            if doc_text:

                find_title = doc_text.find("title")
                if find_title:

                    doc_info["title"] = ' '.join([title_text.strip() for title_text in find_title.stripped_strings])

                    find_body = doc_text.find("body")
                    if find_body:
                        doc_info["body"] = ' '.join([body_text.strip() for body_text in find_body.stripped_strings])
                    else:
                        find_title.next_sibling.strip()

                elif doc_text.string:
                    doc_info["body"] = ' '.join([body_text.strip() for body_text in doc_text.stripped_strings])
                else:
                    doc_info["title"] = doc_info["body"] = None

            else:
                doc_info["body"] = None

            docs.append(doc_info)

        return docs

    def tokenize_docs(self, parsed_docs, process_settings):

        docs_tokens_list = []
        for doc in parsed_docs:
            # tokenizer = tokenize.TweetTokenizer()

            import nltk
            title_tokens = nltk.word_tokenize(doc.get("title")) if doc.get("title") else []
            body_tokens = nltk.word_tokenize(doc.get("body")) if doc.get("body") else []

            doc_tokens = title_tokens + body_tokens

            doc_tokens = Parser.preprocess_tokens(doc_tokens, downcase=process_settings.get("downcase"),
                                                  no_digits=process_settings.get("no_digits"),
                                                  rule_of_thirty=process_settings.get("rule_of_thirty"),
                                                  stop_words_150=process_settings.get("stop_words_150"),
                                                  stemming=process_settings.get("stemming"),
                                                  min_no_char=process_settings.get("min_no_char", 2))

            docs_tokens_list.append({"id": doc.get("id"), "tokens": doc_tokens})

        return docs_tokens_list

    @staticmethod
    def preprocess_tokens(tokens, downcase=True, no_digits=True, rule_of_thirty=True, stop_words_150=False,
                          stemming=True, min_no_char=2):

        final_tokens = tokens

        # Remove punctuation
        punctuation_regexp = re.compile(r"^[,.:;+/\\]+$|^(\\u\d*)$|^(<.*>)$")
        final_tokens = list(filter(lambda token: not punctuation_regexp.match(token), final_tokens))

        # Downcase tokens
        if downcase:
            final_tokens = list(map(lambda token: token.lower(), final_tokens))

        # Remove digits
        if no_digits:
            no_digit_regexp = re.compile(r"[a-zA-Z]+")
            final_tokens = list(filter(lambda token: no_digit_regexp.match(token), final_tokens))

        # Remove 30 stop words
        if rule_of_thirty:
            final_tokens = [token for token in final_tokens if token not in STOP_WORDS_30]

        # Remove 150 stop words
        if stop_words_150:
            final_tokens = [token for token in final_tokens if token not in STOP_WORDS_30_MORE]

        # Stemming
        if stemming:
            stemmer = PorterStemmer()
            final_tokens = list(map(lambda token: stemmer.stem(token, 0, len(token) - 1), final_tokens))

        # More than one character
        if min_no_char > 0:
            final_tokens = list(filter(lambda token: len(token) > min_no_char, final_tokens))

        return final_tokens


class CollectionParser:
    def __init__(self, process_settings=None):
        self.doc_count = 0
        self.token_count = 0
        self.collection_doc_tokens = []
        self.process_settings = process_settings if process_settings is not None else dict()

    def parse_collection(self, token_stream_path, no_docs=2):

        collection_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reuters-data",
                                       "reut2-%03d.sgm")

        parser = Parser()

        for i in range(no_docs):

            try:
                with open(collection_path % i, "r") as reuters_file:
                    file_tokens = parser.parse_file(reuters_file.read(), process_settings=self.process_settings)
            except (OSError, IOError):
                print("Unable to open collection files no. %d" % i)
                exit(1)
            else:
                self.doc_count += len(file_tokens)

                for doc in file_tokens:
                    self.token_count += len(doc.get("tokens"))

                self.collection_doc_tokens += file_tokens

        self.write_collec_disk()

        print("Total no. of docs parsed: %d" % self.doc_count)
        print("Total no. of tokens: %d" % self.token_count)

        token_stream = self.get_token_stream()
        self.save_token_stream(token_stream, token_stream_path)
        return token_stream

    def write_collec_disk(self):

        try:
            save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dict_parsed", "collection.json")
            with open(save_path, "w+") as reuters_file:
                json.dump(self.collection_doc_tokens, reuters_file)
        except (OSError, IOError):
            print("Unable to write collection to disk")
            exit(1)

    def get_token_stream(self):

        token_stream = []

        for doc_token in self.collection_doc_tokens:
            doc_id = doc_token.get("id")
            token_stream.extend(list(map(lambda token: (token, doc_id), doc_token.get("tokens"))))

        return token_stream

    def save_token_stream(self, token_stream, path):

        try:
            with open(path, "w+") as reuters_file:
                reuters_file.writelines(str(token_stream))
        except (OSError, IOError):
            print("Unable to write token stream to disk")
            exit(1)
