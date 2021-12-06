import pandas as pd
import psycopg2 as pg
import pandas as pds
from sqlalchemy import create_engine
from sqlalchemy import create_engine
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


class BooksRecommender(object):
    
        
    def get_books(self, book_name, issued_books, books):
        
            issued_books_with_book_information = issued_books.merge(books, on='book_id')
            book_name=[]
            #create a pivot with column values as book_name and index as userid and value will be books which are issued maximum
            #basically books which are read by user the most are taken for cosine similarity and area_ofstudy will play no role
            user_book_pivot = issued_books_with_book_information.pivot_table(columns='user_id', index='book_name', values="copies_issued")
            user_book_pivot.fillna(0, inplace=True)
            user_book_sparse = csr_matrix(user_book_pivot)
            model = NearestNeighbors(algorithm='brute')
            model.fit(user_book_sparse)

            indx=user_book_pivot.index.values.tolist().index(book_name)
            distances, suggestions = model.kneighbors(user_book_pivot.iloc[indx,: ].values.reshape(1, -1))
            for i in range(len(suggestions)):
                book_name.append(user_book_pivot.index[suggestions[i]])
            return book_name
