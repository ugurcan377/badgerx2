import string

from honey_engine.indexer import Indexer
from honey_engine.utils import tf_idf, normalize


class HoneyEngine(object):

    def __init__(self):
        self.indexer = Indexer()

    def calculate_smilarity(self, query, document):
        intersection = set(query.keys()).intersection(set(document.keys()))
        dot_product = 0
        for term in intersection:
            dot_product += query[term] * document[term]
        return dot_product

    def weight_query(self, query):
        for term, tf in query.items():
            df = self.indexer.df_dict.get('term')
            query[term] = tf_idf(tf, df, self.indexer.N)
        dv = list(query.values())
        for term, tfidf in query.items():
            query[term] = normalize(dv, tfidf)
        return query

    def index_query(self, query_str):
        cleaned_query = query_str.translate(str.maketrans('', '', string.punctuation))
        query_list = cleaned_query.split(' ')
        query_dict = {}
        for term in query_list:
            if self.indexer.df_dict.get(term):
                if query_dict.get(term):
                    query_dict[term] += 1
                else:
                    query_dict[term] = 1

        return self.weight_query(query_dict)

    def rank_documents(self, query):
        results = {}
        for doc_id in range(len(self.indexer.documents)):
            result = self.calculate_smilarity(query, self.indexer.index[str(doc_id)])
            if result != 0:
                results[doc_id] = result
        raw_results = sorted(results, key=results.get, reverse=True)
        return {x: self.indexer.documents[int(x)] for x in raw_results[:30]}

    def execute_query(self, query_str):
        query = self.index_query(query_str)
        return self.rank_documents(query)

    def get_document(self, doc_id, query_str):
        doc_id = int(doc_id)
        corpus = self.indexer.select_source(doc_id)
        name = self.indexer.documents[doc_id]
        document = corpus.raw(name)
        replacements = [("\n", '')] + [(x, "<mark>{}</mark>".format(x)) for x in query_str.split("\n")]
        for old, new in replacements:
            document = document.replace(old, new)
        return name, document