import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from math import log
from sklearn.metrics.pairwise import cosine_similarity


def similarity(doc1, doc2):
    """ Takes two vectorized documents and returns it's similiarity score """
    return cosine_similarity([doc1, doc2])


def preprocess_string(q: str) -> str:
    """Preprocess a string. strips and removes all special characters

    Args:
        q (str): the query string

    Returns:
        str: processed string
    """
    t = []
    q = q.strip().split()
    special = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '{', '}',
               ':', '"', '<', '>', '?', '`', "'", ',', '.', '/', '[', ']']
    for i in q:
        j = i
        for s in special:
            if s in i:
                j = j.replace(s, '')
        if j.isalpha():
            t.append(j.lower())
    return ' '.join(t)


class One2One:
    """Checks similiarity between two documents using Cosine Similiarity
    Method"""

    def __init__(self, filepath1, filepath2, filetype='.txt') -> None:
        self.filepath1 = filepath1
        self.filepath2 = filepath2
        self.filetype = filetype
        self.doc = None

    def setup(self):
        """ Sets up the files for preprocessing """

        base = os.getcwd()

        try:
            abspath = os.path.join(base, self.filepath1)
            if not abspath.endswith(self.filetype):
                abspath += self.filetype

            with open(abspath, 'r', encoding='utf-8') as f:
                self.file1_content = f.read().strip()

            abspath = os.path.join(base, self.filepath2)
            if not abspath.endswith(self.filetype):
                abspath += self.filetype

            with open(abspath, 'r', encoding='utf-8') as f:
                self.file2_content = f.read().strip()

        except FileNotFoundError:
            print("File(s) does not exist")
            sys.exit(0)

    def preprocess_files(self, mode="vector"):
        """ Preprocesses Both the Files as vector and returns it as tuples """

        self.setup()
        self.doc = TfidfVectorizer().fit_transform(
            [self.file1_content, self.file2_content]).toarray()

    def run(self):
        """ Runs the plagiarism Checker and returns the score"""

        if self.doc is None:
            self.preprocess_files()

        self.score = similarity(self.doc[0], self.doc[1])
        return self.score

    def display(self):
        """ Displays the Similiarity Score"""

        print(f"The Similiarity Score for the documents is \
              {round(self.score[0][1]*100, 2)}%")

    def __repr__(self) -> str:
        print(f"{self.filepath1} with {self.filepath2}")


class One2Many:
    """Runs the Plagiarism Check for one query document against
    many source documents. Restricted to only documents search for now.
    """

    def __init__(self, source_path, query_path) -> None:
        self.source_path = source_path
        self.query_path = query_path
        self.source_docs = None
        self.quer = None

    def setup(self, filetype=".txt"):
        """sets up the files for preprocessing
        """

        try:
            base = os.getcwd()
            path = os.path.join(base, self.source_path)

            self.source_files = [doc for doc in os.listdir(path)
                                 if doc.endswith(filetype)]
            self.source_docs = [open(os.path.join(path, _file),
                                     encoding='utf-8').read()
                                for _file in self.source_files]

            query_file = open(self.query_path, 'r', encoding='utf-8')
            self.query = query_file.read()
            query_file.close()

        except FileNotFoundError:
            print("File / Folder does not exist")
            sys.exit(0)

    def preprocess(self):
        """Preprocesses the string for Plagiarism Checker
        """

        self.setup()
        self.collection = [preprocess_string(doc) for doc in self.source_docs]
        self.query = preprocess_string(self.query)

    def normalized_inner_product(self):
        """Collection is a list of strings which contains stripped
        and stemmed list of documents.
        q is the query document which has to be matched against the
        document collection.

        N           -> number of documents in the collection
        n           -> the number of distinct terms in the collection
        f[t]        -> no. of documents containing the term t
        freq[d][t]  -> no. of occurences of term t in document d
        fcount[d]   -> no of distinct terms in document d
        w[d]        -> weight or length of document d
        D           -> Document Collection
        q           -> Query Document
        d           -> A document in collection D
        """

        # Parameter Initialization
        N = len(self.collection)
        W = [0]*(N)

        f = defaultdict(set)
        freq = [defaultdict(int) for i in range(N)]
        fcount = [0]*(N)
        for i in range(N):
            d = self.collection[i].split()
            W[i] = len(d)
            distinct_term_set = set()
            for t in d:
                f[t].add(i)
                freq[i][t] += 1
                distinct_term_set.add(t)
            fcount[i] = len(distinct_term_set)
        # Parameter Initialization Complete. Begin the Processing
        scores = []
        for i in range(N):
            d = self.collection[i].split()
            termset = set(self.query.split()).intersection(set(d))
            sigma = 0
            for t in termset:
                sigma += (1+log(freq[i][t])*(log(1+N/len(f[t]))))
            sigma = 1/(fcount[i]**0.5)*sigma
            scores.append([self.source_files[i], sigma])
        return scores

    def run(self) -> list:
        """Runs the plagiarism Algorithm

        Returns:
            list: description of score with each of the source file
        """
        self.scores = self.normalized_inner_product()
        return self.scores

    def display(self):
        print(f"Plagiarism Score with {self.query_path} is as follows : ")
        print("Document\tScore")

        for name, s in self.scores:
            print(f"{name}\t{round(s,2)}")

    def __repr__(self) -> str:
        print(f"{self.query_path} with {self.source_path}")


class Many2Many:
    """Generate Plagiarism Report for a group of files
    """

    def __init__(self, submission, filetype=".txt") -> None:
        """Creates an instance of Many2Many

        Args:
            submission (str): path for the directory that contains the files
            filetype (str, optional): filetype of files. Defaults to ".txt".
        """

        self.submission = submission
        self.filetype = filetype
        self.collection = None
        self.scores = None

    def setup(self):
        """ Sets up the files for Plagiarism Check """

        try:

            base = os.getcwd()
            path = os.path.join(base, self.submission)

            self.st_files = [doc for doc in os.listdir(path)
                             if doc.endswith(self.filetype)]
            self.source_docs = [open(os.path.join(path, _file),
                                     encoding='utf-8').read()
                                for _file in self.st_files]

        except FileNotFoundError:
            print("File / Folder does not exist")
            sys.exit(0)

    def preprocess(self):
        """Preprocesses all the files as vectors
        """

        self.setup()
        self.collection = TfidfVectorizer().fit_transform(
            self.source_docs).toarray()

    def run(self, threshold=0.6) -> list:
        """Runs the Plagiarism Checker among all the files in given folder

        Args:
            threshold (float, optional): Minimum similiarity threshold
            to consider plagiarized. Defaults to 0.6.

        Returns:
            list: the plagiarism report of all the files.
        """

        if self.collection is None:
            self.preprocess()

        st_vectors = list(zip(self.st_files, self.collection))

        results = set()
        for file1, text1 in st_vectors:
            new_vectors = st_vectors.copy()
            current_index = new_vectors.index((file1, text1))
            new_vectors.pop(current_index)
            for file2, text2 in new_vectors:
                score = similarity(text1, text2)[0][1]
                if score < threshold:
                    continue

                st_pair = sorted((file1, file2))
                score = (st_pair[0], st_pair[1], score)
                results.add(score)
        self.res = list(results)
        self.res.sort(key=lambda x: x[2], reverse=True)
        return self.res

    def display(self):
        """Displays the Plagiarism Result in a Orderly Manner
        """

        print(" ==================  Result ====================")
        for a, b, c in self.res:
            print(f"{a}\t{b}\t{c*100}%")


