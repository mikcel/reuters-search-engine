import json
import traceback

import sys
import shutil
import os
from collections import OrderedDict

try:
    import cPickle as pickle
except:
    import pickle


class IndexConstructor:
    def __init__(self, token_stream, block_size=10240):
        self.token_stream = token_stream
        self.block_size = block_size
        self.block_no = 1
        self.tmp_file_dir_path = os.path.join(os.path.abspath(os.path.dirname(os.path.relpath(__file__))),
                                              "tmp_block_dir")
        self.inverted_index_path = os.path.join(os.path.relpath(__file__), "..", "..", "parsed_data", "inverted_index.bin")
        self.inverted_index = OrderedDict()

    def construct_index(self, clear_tmp=True, get_stats=False, save_json=False):

        print("Making new directory for blocks' file")
        self.__clear_tmp_block_dir()
        self.__make_tmp_block_dir()

        print("Inverting the block files with SPIMI")
        self.spimi_invert()

        print("Merging the blocks to make index")
        self.merge_blocks()

        if clear_tmp:
            print("Clearing temporary folder for the blocks file")
            self.__clear_tmp_block_dir()
            self.__dump_inverted_index()

        if save_json:
            self.save_index_json()

        if get_stats:
            self.get_stats()

        return self.inverted_index_path

    def spimi_invert(self):

        list_idx = 0

        # Make sure to go through all tokens
        while self.__check_idx(list_idx):

            block_dict = dict()

            # Make sure to respect block size and that list indexing does not overflow
            while self.__get_dump_size(block_dict) < self.block_size and self.__check_idx(list_idx):

                token_pair = self.token_stream[list_idx]
                term, doc_id = token_pair[0], int(token_pair[1])
                term_posting_list = []
                if term not in block_dict:
                    block_dict[term] = term_posting_list
                else:
                    term_posting_list = block_dict[term]

                if doc_id not in term_posting_list:
                    term_posting_list.insert(len(term_posting_list), doc_id)

                list_idx += 1

            sorted_terms = sorted(block_dict)

            self.save_block_data(sorted_terms, block_dict)
            self.block_no += 1

    def merge_blocks(self):

        file_list = self.get_sorted_block_files()
        tmp_inverted_idx = dict()

        for block_file in file_list:

            try:
                with open(os.path.join(self.tmp_file_dir_path, block_file[1]), "rb") as file_obj:
                    sorted_terms = pickle.load(file_obj)
                    block_dict = pickle.load(file_obj)
            except (IOError, OSError):
                print("Unable to load block file")
                exit(1)
            else:
                for term in sorted_terms:
                    if term not in tmp_inverted_idx:
                        tmp_inverted_idx[term] = block_dict[term]
                    else:
                        tmp_inverted_idx[term] = self.merge_postings_list(tmp_inverted_idx[term], block_dict[term])

        for term in sorted(tmp_inverted_idx):
            self.inverted_index[term] = tmp_inverted_idx[term]

    def get_sorted_block_files(self):

        files = os.listdir(self.tmp_file_dir_path)
        file_pairs = list()
        for file in files:
            file_path = os.path.join(self.tmp_file_dir_path, file)
            file_pairs.append((os.path.getsize(file_path), file))

        file_pairs.sort(key=lambda pair: pair[0])

        return file_pairs

    def merge_postings_list(self, first_list, second_list):

        iter_first_list = iter(first_list)
        iter_scnd_list = iter(second_list)

        first_list_post = next(iter_first_list, None)
        scnd_list_post = next(iter_scnd_list, None)

        merged_list = list()
        while first_list_post is not None and scnd_list_post is not None:

            if first_list_post == scnd_list_post:
                merged_list.append(first_list_post)
                first_list_post = next(iter_first_list, None)
                scnd_list_post = next(iter_scnd_list, None)

            elif first_list_post < scnd_list_post:
                merged_list.append(first_list_post)
                first_list_post = next(iter_first_list, None)

            else:
                merged_list.append(scnd_list_post)
                scnd_list_post = next(iter_scnd_list, None)

        if first_list_post is not None:
            merged_list += first_list[first_list.index(first_list_post):]
        elif scnd_list_post is not None:
            merged_list += second_list[second_list.index(scnd_list_post):]

        return merged_list

    def save_block_data(self, sorted_keys, block_dict):

        block_path = os.path.join(self.tmp_file_dir_path, "block_%05d.bin" % self.block_no)

        try:
            with open(block_path, "wb") as tmp_file:
                self.__dump_pickle(sorted_keys, tmp_file)
                self.__dump_pickle(block_dict, tmp_file)
        except (IOError, OSError):
            print("Error saving block file")
            exit(1)

    def get_stats(self):

        print("No. of distinct terms: %d" % len(self.inverted_index))

        postings_count = sum(len(post_list) for post_list in self.inverted_index.values())
        print("No. of nonpositional postings: %d" % postings_count)

    def save_index_json(self):
        try:
            with open(os.path.join(os.path.relpath(__file__), "..", "..", "parsed_data", "inverted_index.json"), "w") as dump_file:
                json.dump(self.inverted_index, dump_file)
        except (IOError, OSError):
            print("Unable to dump inverted index (JSON)")
            exit(1)

    def __clear_tmp_block_dir(self):

        if os.path.exists(self.tmp_file_dir_path):
            shutil.rmtree(self.tmp_file_dir_path)

    def __make_tmp_block_dir(self):
        os.makedirs(self.tmp_file_dir_path)

    def __dump_pickle(self, obj, file_obj):
        pickle.dump(obj=obj, file=file_obj, protocol=pickle.HIGHEST_PROTOCOL)

    def __get_dump_size(self, dict_obj):
        terms_size = sys.getsizeof(pickle.dumps(list(dict_obj.keys())))
        whole_dict_size = sys.getsizeof(pickle.dumps(dict_obj, pickle.HIGHEST_PROTOCOL))
        return terms_size + whole_dict_size

    def __check_idx(self, list_idx):
        return list_idx < len(self.token_stream)

    def __dump_inverted_index(self):
        try:
            with open(self.inverted_index_path, "wb") as dump_file:
                self.__dump_pickle(self.inverted_index, dump_file)
        except (IOError, OSError):
            print("Unable to dump inverted index")
            exit(1)
