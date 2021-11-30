class matrix_algebra:
    
    def _init_(self, add, subtract, multiply, dotp):
        '''General distribution for basic matrix calculation using
        general python functions
        
        Attributes: 
        add: Addition of two matrices
        subtract: Subtraction of two matrices
        multiply: Multiplication of two matrices
        invert: Inversion of a matrix'''
        
        
        self.add = add
        self.subtract = subtract
        self.multiply = multiply
        self.invert = invert
        
    def calculate_add(self, mat_A, mat_B):
        '''Addition of two matrices
        Args:
        mat_A: a matrix of dimension [i, j]
        mat_B: a matrix of dimension [i, j]
        
        Returns: Matrix addition results in a new matrix of dimension [i, j]'''
        addition = [[mat_A[i][j]+mat_B[i][j] for j in range(len(mat_B[0]))] for i in range(len(mat_A))]
        self.add = addition
        return self.add
    
    def calculate_subtract(self, mat_A, mat_B):
        '''Subtraction of two matrices
        Args:
        mat_A: a matrix of dimension [i, j]
        mat_B: a matrix of dimension [i, j]
        
        Returns: Matrix addition results in a new matrix of dimension [i, j]'''    
        subtraction = [[mat_A[i][j]-mat_B[i][j] for j in range(len(mat_B[0]))] for i in range(len(mat_A))]
        self.subtract = subtraction
        return self.subtract
    
    def  calculate_multiplication(self, mat_A, mat_B):
        '''Multiplication of two matrices
        Args:
        mat_A: a matrix of dimension [i, j]
        mat_B: a matrix of dimension [j, k]
        
        Returns: Matrix addition results in a new matrix of dimension [i, k]'''
        
        multiplication = [[sum(mat_A[i][j]*mat_B[j][k] for j in range(len(mat_B))) for k in range(len(mat_B[0]))] for i in       range(len(mat_A))]
        self.multiply = multiplication
        return self.multiply
    
    def calculate_dotproduct(self, mat_A, vect_B):
        '''Multiplication of a vector by a matrix is done by using dot product method
        Args:
        mat_A = a matrix of dimension [i, j]
        vect_B = a vector of dimension j
        
        Returns: Multiplication of a vector by a matrix'''
        result = [sum(mat_A[i][j]*vect_B[j] for j in range(len(vect_B))) for i in range(len(mat_A))]
        self.dotp = result
        return self.dotp
    
