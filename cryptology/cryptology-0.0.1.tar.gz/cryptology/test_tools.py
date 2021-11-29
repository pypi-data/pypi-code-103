import unittest

from tools import (type_str_error,
                   type_alphabet_error,
                   type_int_error,
                   type_duplicate_letter_error,
                   get_pos_alphabet,
                   get_atbashed_pos_alphabet,
                   get_alphabet_from_pos,
                   get_ceaser_pos,
                   get_ceaser_pos_decrypt,
                   order_alpha,
                   vigenere_permutation,
                   create_viginere_table,
                   keyword_text_match_up,
                   viginere_get_table_decrypt,
                   viginere_get_table_encrypt,
                   playfair_grid_list,
                   playfair_deal_with_dups,
                   get_play_fair_row_col,
                   playfair_put_into_pairs,
                   playfair_decrypt_pair,
                   playfair_encrypt_row_pair,
                   playfair_decrypt_row_pair,
                   playfair_decrypt_col_pair,
                   playfair_encrypt_col_pair,
                   playfair_decrypt_rectangle,
                   playfair_encrypt_rectangle,
                   unpack_list_of_tuples)

class test_tools(unittest.TestCase):

    def test_type_str_error(self):
        
        self.assertRaises(TypeError, type_str_error, 2)
        self.assertRaises(TypeError, type_str_error, ["A"])
        self.assertRaises(TypeError, type_str_error, ("A", "B", "C"))
        
    def test_type_alphabet_error(self):
        
        self.assertRaises(TypeError, type_alphabet_error, "3")
        self.assertRaises(TypeError, type_alphabet_error, ["!?@"])
    
    def test_type_duplicate_letter_error(self):
        
        self.assertRaises(TypeError, type_duplicate_letter_error, "AA")
        
        
    def test_get_pos_alphabet(self):
        
        sample=["A","V", "F"]
        
        expected=[0, 21, 5]
        
        result=get_pos_alphabet(sample)
        
        self.assertListEqual(expected, result)
        
    def test_get_atbash_decrypt_pos_alphabet(self):
        
        sample=[0, 21, 5]
        
        expected=[25,4,20]
        
        result=get_atbashed_pos_alphabet(sample)
        
        self.assertListEqual(expected, result)
    
    def test_get_alphabet_from_pos(self):
        
        sample=[25,4,20]
        
        expected=["Z", "E", "U"]
        
        result=get_alphabet_from_pos(sample)
        
        self.assertListEqual(expected, result)

    def test_type_int_error(self):

        self.assertRaises(TypeError, type_int_error, "2")
        self.assertRaises(TypeError, type_int_error, ["A"])
        self.assertRaises(TypeError, type_int_error, ("A", "B", "C"))

    def test_get_ceaser_pos(self):

        sample=[4,25,14,11,9]
    

        result=get_ceaser_pos(letters_pos=sample,
                        shift=11)

        expected=[19,14,3,0,24]

        self.assertListEqual(result, expected)

    def test_get_ceaser_pos_decrypt(self):

        
        sample=[19,14,3,0,24]
    

        result=get_ceaser_pos_decrypt(letters_pos=sample,
                        shift=11)

       
        expected=[4,25,14,11,9]

        self.assertListEqual(result, expected)

    def test_order_alpha(self):
        
        input_var="D"
        
        result=order_alpha(input_var)
        
        expected=['D','E','F','G','H','I','J','K','L','M','N','O','P',
                  'Q','R','S','T','U','V','W','X','Y','Z','A','B','C']

        self.assertListEqual(result, expected)
        
    def test_vigenere_permutation(self):
        
        input_var="SWAN"
        
        result=vigenere_permutation("SWAN")
        
        expected=['S','W','A','N','B','C','D','E','F','G','H','I','J',
                  'K','L','M','O','P','Q','R','T','U','V','X','Y','Z']
        
        self.assertListEqual(result, expected)        
        
    def test_create_viginere_table(self):
        
        input_var="THISLEPGYWNOMARKDBFCJQUVXZ"
        
        result=create_viginere_table(input_var)
        
        expected={'A': ['T','H','I','S','L','E','P','G','Y','W','N','O','M',
                        'A','R','K','D','B','F','C','J','Q','U','V','X','Z'],
                  'B': ['H','I','S','L','E','P','G','Y','W','N','O','M','A',
                        'R','K','D','B','F','C','J','Q','U','V','X','Z','T'],
                  'C': ['I','S','L','E','P','G','Y','W','N','O','M','A','R',
                        'K','D','B','F','C','J','Q','U','V','X','Z','T','H'],
                  'D': ['S','L','E','P','G','Y','W','N','O','M','A','R','K',
                        'D','B','F','C','J','Q','U','V','X','Z','T','H','I'],
                  'E': ['L','E','P','G','Y','W','N','O','M','A','R','K','D',
                        'B','F','C','J','Q','U','V','X','Z','T','H','I','S'],
                  'F': ['E','P','G','Y','W','N','O','M','A','R','K','D','B',
                        'F','C','J','Q','U','V','X','Z','T','H','I','S','L'],
                  'G': ['P','G','Y','W','N','O','M','A','R','K','D','B','F',
                        'C','J','Q','U','V','X','Z','T','H','I','S','L','E'],
                  'H': ['G','Y','W','N','O','M','A','R','K','D','B','F','C',
                        'J','Q','U','V','X','Z','T','H','I','S','L','E','P'],
                  'I': ['Y','W','N','O','M','A','R','K','D','B','F','C','J',
                        'Q','U','V','X','Z','T','H','I','S','L','E','P','G'],
                  'J': ['W','N','O','M','A','R','K','D','B','F','C','J','Q',
                        'U','V','X','Z','T','H','I','S','L','E','P','G','Y'],
                  'K': ['N', 'O','M','A','R','K','D','B','F','C','J','Q','U',
                        'V','X','Z','T','H','I','S','L','E','P','G','Y','W'],
                  'L': ['O','M','A','R','K','D','B','F','C','J','Q','U','V',
                        'X','Z','T','H','I','S','L','E','P','G','Y','W','N'],
                  'M': ['M','A','R','K','D','B','F','C','J','Q','U','V','X',
                        'Z','T','H','I','S','L','E','P','G','Y','W','N','O'],
                  'N': ['A','R','K','D','B','F','C','J','Q','U','V','X','Z',
                        'T','H','I','S','L','E','P','G','Y','W','N','O','M'],
                  'O': ['R','K','D','B','F','C','J','Q','U','V','X','Z','T',
                        'H','I','S','L','E','P','G','Y','W','N','O','M','A'],
                  'P': ['K','D','B','F','C','J','Q','U','V','X','Z','T','H',
                        'I','S','L','E','P','G','Y','W','N','O','M','A','R'],
                  'Q': ['D','B','F','C','J','Q','U','V','X','Z','T','H','I',
                        'S','L','E','P','G','Y','W','N','O','M','A','R','K'],
                  'R': ['B','F','C','J','Q','U','V','X','Z','T','H','I','S',
                        'L','E','P','G','Y','W','N','O','M','A','R','K','D'],
                  'S': ['F','C','J','Q','U','V','X','Z','T','H','I','S','L',
                        'E','P','G','Y','W','N','O','M','A','R','K','D','B'],
                  'T': ['C','J','Q','U','V','X','Z','T','H','I','S','L','E',
                        'P','G','Y','W','N','O','M','A','R','K','D','B','F'],
                  'U': ['J','Q','U','V','X','Z','T','H','I','S','L','E','P',
                        'G','Y','W','N','O','M','A','R','K','D','B','F','C'],
                  'V': ['Q','U','V','X','Z','T','H','I','S','L','E','P','G',
                        'Y','W','N','O','M','A','R','K','D','B','F','C','J'],
                  'W': ['U','V','X','Z','T','H','I','S','L','E','P','G','Y',
                        'W','N','O','M','A','R','K','D','B','F','C','J','Q'],
                  'X': ['V','X','Z','T','H','I','S','L','E','P','G','Y','W',
                        'N','O','M','A','R','K','D','B','F','C','J','Q','U'],
                  'Y': ['X','Z','T','H','I','S','L','E','P','G','Y','W','N',
                        'O','M','A','R','K','D','B','F','C','J','Q','U','V'],
                  'Z': ['Z','T','H','I','S','L','E','P','G','Y','W','N','O',
                        'M','A','R','K','D','B','F','C','J','Q','U','V','X']}   
        
        self.maxDiff=None
        self.assertDictEqual(expected, result)
        
    def test_keyword_text_match_up(self):
        
        result1,result2=keyword_text_match_up(text="FGQVEQYONMCCHAXTPBAC", 
                              keyword="FAMILY")      
    
        expected1=['F','A','M','I','L','Y','F','A','M','I','L','Y',
                  'F','A','M','I','L','Y','F','A']
        
        expected2=['F','G','Q','V','E','Q','Y','O','N','M','C',
                   'C','H','A','X','T','P','B','A','C']
        
        self.assertEqual(result1, expected1)
        self.assertEqual(result2, expected2)
    
    def test_viginere_get_table_decrypt(self):
        
        vigin_table=create_viginere_table("") 
        result=viginere_get_table_decrypt(table=vigin_table,
                                          keyword_letter="M",
                                          text_letter="Q")
        
        expected="E"
        
        self.assertEqual(result, expected)
        
    def test_viginere_get_table_encrypt(self):
        
        vigin_table=create_viginere_table("") 
        result=viginere_get_table_encrypt(table=vigin_table,
                                          keyword_letter="Y",
                                          text_letter="S")
        
        expected="Q"
        
        self.assertEqual(result, expected)
        
    def test_playfair_grid_list(self):
        
        input_var="GLAMORGAN"
        
        result=playfair_grid_list(keyword=input_var)
        
        expected=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']
        
        self.assertEqual(result, expected)
        
    def test_playfair_deal_with_dups(self):
        
        input_var="MEETMEATTREFFORESTSTATION"
        
        result=playfair_deal_with_dups(input_var)
        
        expected=["M","E","X","E","T","M","E","A","T","X","T","R","E","F","X",
                  "F","O","R","E","S","T","S","T","A","T","I","O","N"]
                
        self.assertEqual(result, expected)
        
    def test_get_play_fair_row_col(self):
        
        input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']
        
        result=get_play_fair_row_col(playfair_grid=input_var,
                                     letter="S")
        
        expected=(3,2)
        
        self.assertEqual(result, expected)

    def test_playfair_put_into_pairs(self):

        input_var=["A","B","C"]    

        result=playfair_put_into_pairs(text=input_var)

        expected=["AB","CX"]

        self.assertEqual(result, expected)

    def test_decrypt_pair(self):

      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']

      result_1=playfair_decrypt_pair(playfair_list=input_var, 
                        pair="GP")

      result_2=playfair_decrypt_pair(playfair_list=input_var, 
                        pair="FI")

                        
      result_3=playfair_decrypt_pair(playfair_list=input_var, 
                        pair="MF")

      expected_1=("V","E")
      expected_2=("E","H")
      expected_3=("L","I")

      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)
      self.assertEqual(result_3, expected_3)

    def test_playfair_decrpt_row_pair(self):     

      
      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']

      result_1=playfair_decrypt_row_pair(grid=input_var, 
                     pair="QT")
            
      result_2=playfair_decrypt_row_pair(grid=input_var, 
                     pair="EK")

      result_3=playfair_decrypt_row_pair(grid=input_var, 
                     pair="GL")

      result_4=playfair_decrypt_row_pair(grid=input_var, 
                     pair="VZ")


      expected_1=("P","S")
      expected_2=("K","I")
      expected_3=("O","G")
      expected_4=("Z","Y")
            
      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)
      self.assertEqual(result_3, expected_3)

    def test_playfair_decrpt_col_pair(self):     

      
      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']

      result_1=playfair_decrypt_col_pair(grid=input_var, 
                     pair="LN")
            
      result_2=playfair_decrypt_col_pair(grid=input_var, 
                     pair="TC")

      expected_1=("W","L")
      expected_2=("I","M")
            
      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)

    def test_playfair_decrypt_rectangle(self):

      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']

      result_1=playfair_decrypt_rectangle(grid=input_var, 
                                          x_1=0,
                                          y_1=3,
                                          x_2=2,
                                          y_2=1)
            
      result_2=playfair_decrypt_rectangle(grid=input_var, 
                                          x_1=0,
                                          y_1=0,
                                          x_2=1,
                                          y_2=1)

      expected_1=("L","I")
      expected_2=("L","R")
            
      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)

    def test_unpack_list_of_tuples(self):

      input_var=[("A","B"),("C","D")]
      result=unpack_list_of_tuples(list_tuples=input_var)

      expected=["A","B","C","D"]

      self.assertEqual(result, expected)

    def test_playfair_encrypt_row_pair(self):

      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']
          
      result_1=playfair_encrypt_row_pair(grid=input_var,
                                    pair="AM")

      result_2=playfair_encrypt_row_pair(grid=input_var,
                                    pair="GO")

      result_3=playfair_encrypt_row_pair(grid=input_var,
                                    pair="VZ")

      expected_1=("M","O")                    
      expected_2=("L","G")
      expected_3=("W","V")


      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)
      self.assertEqual(result_3, expected_3)

    def test_playfair_encrypt_col_pair(self):

      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']
          
      result_1=playfair_encrypt_col_pair(grid=input_var,
                                    pair="NF")

      result_2=playfair_encrypt_col_pair(grid=input_var,
                                    pair="MY")

      result_3=playfair_encrypt_col_pair(grid=input_var,
                                    pair="EP")

      expected_1=("F","Q")                    
      expected_2=("C","M")
      expected_3=("P","V")


      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)
      self.assertEqual(result_3, expected_3)

    def test_playfair_encrypt_rectangle(self):

      input_var=['G','L','A','M','O','R','N','B','C','D','E','F','H',
                  'I','K','P','Q','S','T','U','V','W','X','Y','Z']
          
      result_1=playfair_encrypt_rectangle(grid=input_var,
                                          x_1=2,
                                          y_1=0,
                                          x_2=0,
                                          y_2=2)

      result_2=playfair_encrypt_rectangle(grid=input_var,
                                          x_1=3,
                                          y_1=3,
                                          x_2=4,
                                          y_2=2)

      result_3=playfair_encrypt_rectangle(grid=input_var,
                                          x_1=3,
                                          y_1=3,
                                          x_2=1,
                                          y_2=0)
                                   
      expected_1=("H","G")                    
      expected_2=("S","Y")
      expected_3=("P","C")


      self.assertEqual(result_1, expected_1)
      self.assertEqual(result_2, expected_2)
      self.assertEqual(result_3, expected_3)

      



if __name__=="__main__":
    unittest.main()


        
        
    