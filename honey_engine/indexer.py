import json
import string

from nltk import corpus

from honey_engine.utils import tf_idf, normalize


class Indexer(object):

    def __init__(self):
        self.stopwords = ['a', 'the', 's']
        self.N = 0
        self.documents = []
        self.doc_index = []
        self.prepare_documents()
        self.check_for_index()

    def prepare_documents(self):
        self.documents = corpus.gutenberg.fileids() + corpus.inaugural.fileids() +\
               corpus.state_union.fileids() + corpus.reuters.fileids() + corpus.brown.fileids()
        self.doc_index = [(0, 'gutenberg'), (18, 'inaugural'), (74, 'state_union'),
                          (139, 'reuters'), (10927, 'brown'), (11427, None)]

    def check_for_index(self):
        try:
            self.index = json.load(open('../honey_engine/index.json'))
            self.df_dict = json.load(open('../honey_engine/dfindex.json'))
            self.N = self.df_dict["N"]
        except IOError:
            self.index = {}
            self.df_dict = {}
            self.create_index()

    def save_index(self):
        json.dump(self.index, open('index.json', 'w'))
        json.dump(self.df_dict, open('dfindex.json', 'w'))

    def index_document(self, doc_id, document):
        self.index[doc_id] = {}
        for line in document:
            fline = [x.translate(str.maketrans("", "", string.punctuation)) for x in line if line not in self.stopwords]
            for term in fline:
                if self.index[doc_id].get(term):
                    self.N += 1
                    if self.index[doc_id].get(term):
                        self.index[doc_id][term] += 1
                    else:
                        self.index[doc_id][term] = 1
                        self.df_dict[term] += 1
                else:
                    self.index[doc_id][term] = 1
                    self.df_dict[term] = 1

    def create_index(self):
        thres, name = self.doc_index[0]
        next_index = 1
        source = None
        for doc_id, document in enumerate(self.documents):
            if doc_id == thres:
                source = getattr(corpus, name)
                thres, name = self.doc_index[next_index]
                next_index += 1
            self.index_document(str(doc_id), source.sents(document))
        self.df_dict["N"] = self.N
        self.weight_index()
        self.save_index()

    def weight_index(self):
        for doc_id, document in self.index.items():
            for term, tf in document.items():
                df = self.df_dict.get(term)
                self.index[doc_id][term] = tf_idf(tf, df, self.N)
            dv = list(document.values())
            for term, tfidf in document.items():
                self.index[doc_id][term] = normalize(dv, tfidf)

    def select_source(self, doc_id):
        result = ''
        for thres, source in self.doc_index:
            if doc_id > thres:
                result = source
        return getattr(corpus, result)