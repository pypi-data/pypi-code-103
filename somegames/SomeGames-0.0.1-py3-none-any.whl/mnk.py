import numpy as np

class _Gameboard:

    def __init__(self):
        self._game_board = self._construct_game_board()
        self._board = [" "]*9
        self._filled_cells = {"O":[], "X":[]}
        
    def _construct_game_board(self):
        separator = " ———" * 3 + "\n"
        cell_info = "| {} " * 3 + "|\n"
        return (separator + cell_info) * 3  + separator
    
    def _show_progress(self):
        print(self._game_board.format(*self._board))

    



class _TicTacToe(_Gameboard):
    
    def __init__(self):
        super().__init__()
        self._round = 0
        self._msg = ""
        
    def play_game(self):
        self._print_instructions()
        while True:
            self._get_input()
            self._update_board()
            self._show_progress()
            if self._game_over():
                break
            self._round += 1
        self._ending_prompt()
        
    def _print_instructions(self):
        print("This is a game of Tic-Tac-Toe.")
        print("There are two players, O and X, and the O-player moves first.")
        print("The player who succeeds in placing 3 of their marks in a horizontal, vertical, or \
diagonal row is the winner.\n")
        self._show_progress()
            
    def _get_input(self):
        self._msg = ""
        ans = input(self._get_prompt_message())
        while self._is_invalid_input(ans):
            ans = input(self._get_prompt_message())              
            
    def _update_board(self):
        current_player = self._get_current_player()
        # get the coordinates of the last input
        x,y = self._filled_cells[current_player][-1]
        # since the input numbering starts from 1 (not 0), both x,y must be decreased by 1 to match 
        # Python's numbering conventions and update the board with the current player's last input
        self._board[3*(x-1)+(y-1)] = current_player

    def _game_over(self):
        if " " not in self._board:
            return True
        else:
            return self._we_have_a_winner()
            
    def _ending_prompt(self):
        print("Game Over!", end=" ")
        if self._we_have_a_winner():
            print("{}-player Wins!".format(self._get_current_player()))
        else:
            print("It's a Tie!")
    
    def _get_prompt_message(self):
        if self._msg == "":
            msg1,msg2 = "",""
        elif self._msg == "already filled":
            msg1,msg2 = "That cell is already filled. ", "valid "
        else:
            msg1,msg2 = "Must enter two integers separated by a comma. ", "valid "
        return "{}{}-player enter a {}location on the board (x,y): ".format(msg1, self._get_current_player(), msg2)
    
    def _is_invalid_input(self, ans):
        try:
            # the input must be a coordinate on the board separated by a comma
            correct_input = self._read_input(ans)
        except:
            return True
        # since it has to be a coordinate on the board, correct_input must have length=2
        # also the newly entered coordinates cannot be already filled on the board
        if self._not_already_filled(correct_input):
            self._filled_cells[self._get_current_player()].append(correct_input)
            return False
        else:
            self._msg = "already filled"
            return True
        
    def _get_current_player(self):
        return "O" if self._round % 2 == 0 else "X"
    
    def _we_have_a_winner(self):
        # to utilize a simple numpy counting function, convert the current player's filled cell locations
        # into a numpy array
        arr = np.array(self._filled_cells[self._get_current_player()])
        if self._we_have_a_horizontal_or_vertical_winner(arr):
            return True
        elif self._we_have_a_diagonal_winner(arr):
            return True
        else:
            return False
        
    def _read_input(self, ans):
        new_input = [int(s) for s in ans.strip("()").split(",") if 1<=int(s)<=3]
        if len(new_input) == 2:
            return new_input
        else:
            self._msg = "not tuple"
            raise ValueError("")
        
    def _not_already_filled(self, new_input):
        return True if len(self._filled_cells) == 0 else (new_input not in self._flattened_filled_cells())
    
    def _flattened_filled_cells(self):
        x = list(self._filled_cells.values())
        return x[0] + x[1]
    
    def _we_have_a_horizontal_or_vertical_winner(self, arr):
        for i in range(2):
            if (np.bincount(arr[:,i])==3).any():
                return True

    def _we_have_a_diagonal_winner(self, arr):
        if np.sum(arr[:,0]==arr[:,1]) == 3:
            return True
        elif np.sum(np.sum(arr, axis=1)==4) == 3:
            return True
        else:
            return False
    



class _mnk(_TicTacToe):
    
    def __init__(self, m, n, k):
        self._width = n
        self._height = m
        self._winning_length = k
        self._validate_input()
        super().__init__()
        self._game_board = self._construct_game_board()
        self._board = [" "]*(self._height*self._width)
        
    def _validate_input(self):
        if not isinstance(self._height, int):
            raise TypeError('"m" must be an integer.')
        if not isinstance(self._width, int):
            raise TypeError('"n" must be an integer.')
        if not isinstance(self._winning_length, int):
            raise TypeError('"k" must be an integer.')
        if self._winning_length > min(self._width,self._height):
            raise ValueError('"k" cannot be greater than "m" or "n".')
        
    def _print_instructions(self):
        print("This is (m,n,k)-Game. Your selected board size is {}x{} (shown below).".format(self._height, self._width))
        print("There are two players, O and X, and the O-player moves first.")
        print("The player who succeeds in placing {} of their marks in a horizontal, vertical, or \
diagonal row is the winner.\n".format(self._winning_length))
        self._show_progress()

    def _construct_game_board(self):
        sep = " --- " + " ———" * self._width + "\n"
        cell_info = "| {} " * self._width + "|\n"
        table = "".join([(sep + "  " + self._get_idx_format(i+1) + "|" + cell_info) for i in range(self._height)]) + sep
        head_sep = "     " + " ---" * self._width + "\n"
        header = (head_sep + "(x,y)| " + "| ".join([self._get_idx_format(i) for i in range(1,self._width+1)]) 
                  + "|\n" + head_sep)
        return header + table

    def _update_board(self):
        current_player = self._get_current_player()
        # get the coordinates of the last input
        x,y = self._filled_cells[current_player][-1]
        # since the input numbering starts from 1 (not 0), both x,y must be decreased by 1 to match 
        # Python's numbering conventions and update the board with the current player's last input
        self._board[self._width*(x-1)+(y-1)] = current_player
              
    def _read_input(self, ans):
        new_input =  ans.strip("()").split(",")
        if (len(new_input) == 2) and all(1 <= int(i) <= j for i,j in zip(new_input, [self._height, self._width])):
            return [int(s) for s in new_input]
        else:
            self._msg = "not tuple"
            raise ValueError("")

    
    def _we_have_a_diagonal_winner(self, arr):
        #check the topleft to rightbottom diagonals
        for diff in range(self._winning_length-self._width, self._height-self._winning_length+1):
            sub_arr = np.sort(arr[arr[:,0] - diff == arr[:,1], 0])
            if self._k_consecutive_cells_filled(sub_arr):
                return True
        #check the topright to leftbottom diagonals
        for total in range(self._winning_length+1, self._height+self._width-self._winning_length+2):
            sub_arr = np.sort(arr[arr[:,0] + arr[:,1] == total, 0])
            if self._k_consecutive_cells_filled(sub_arr):
                return True
        return False
    
    def _k_consecutive_cells_filled(self, arr):
        slicing_indexes = np.where(np.diff(arr) != 1)[0] + 1
        splits = np.split(arr, slicing_indexes)
        for split in splits:
            if len(split) >= self._winning_length:
                return True
    
    def _we_have_a_horizontal_or_vertical_winner(self, arr):
        if self._horizontal_or_vertical_winner_found(arr,1,0):
            return True
        elif self._horizontal_or_vertical_winner_found(arr,0,1):
            return True
        else:
            return False
    
    def _horizontal_or_vertical_winner_found(self, arr, i, j):
        # sort by ith column
        sorted_arr = arr[arr[:, i].argsort()]
        # split the sorted arr by the unique values in the ith column
        splits = np.split(sorted_arr, np.unique(sorted_arr[:, i], return_index=True)[1], axis=0)[1:]
        # then for each split sub_array, sort the jth column and check if k consecutive cells are filled 
        # (it means that either horizontally or vertically, k consecutive cells are filled)
        for split in splits:
            horizontal_or_vertical_axis = np.sort(split[:, j])
            if self._k_consecutive_cells_filled(horizontal_or_vertical_axis):
                return True
    
    def _get_idx_format(self, i):
        return ("{} " if i<10 else "{}").format(i)



def TicTacToe():
    """
    This is a function that implements Tic-Tac-Toe, which is a board game in which 
    two players ("O" and "X") take turns in placing their mark on a 3-by-3 board. 
    The winner is the player who first gets 3 of their marks in a row, horizontally, 
    vertically, or diagonally (https://en.wikipedia.org/wiki/Tic-tac-toe).
    Note that "O"-player moves first.
    Upon running the function, a prompt appears first asking the "O"-player to enter a 
    location on the board. Since the location must be a coordinate on the board, it 
    must be a tuple, separated by a comma, e.g. (x,y), where 1<=x<=3, 1<=y<=3. 
    When the "O"-player enters a location on the board (not yet occupied by a mark), "O" 
    is placed on that location and a prompt appears again asking for the "X"-player to 
    enter a location on the board. Their entry cannot be a cell already occupied by a 
    mark.
    The game continues until every cell is occupied or a winner is determined.
    ------------------------------------------------------------------------------------
    Parameters: None
    -------------------------------------------------------------------------------------
    Returns: None
    -------------------------------------------------------------------------------------
    Example:
    TicTacToe()
    """
    _TicTacToe().play_game()
    

def mnkGame(m=4,n=5,k=3):
    """
    This is a function that implements the m,n,k-game, which is a board game in which 
    two players ("O" and "X") take turns in placing their mark on an m-by-n board. 
    The winner is the player who first gets k of their marks in a row, horizontally, 
    vertically, or diagonally (https://en.wikipedia.org/wiki/M,n,k-game).
    Note that "O"-player moves first.
    Upon running the function, a prompt appears first asking the "O"-player to enter a 
    location on the board. Since the location must be a coordinate on the board, it 
    must be a tuple, separated by a comma, e.g. (x,y), where 1<=x<=m, 1<=y<=n. Moreover, 
    k must be no greater than the minimum of m and n. 
    When the "O"-player enters a location on the board (not yet occupied by a mark), "O" 
    is placed on that location and a prompt appears again asking for the "X"-player to 
    enter a location on the board. Their entry cannot be a cell already occupied by a 
    mark.
    The game continues until every cell is occupied or a winner is determined.
    ------------------------------------------------------------------------------------
    Parameters:
    -----------
    m: int, default: 4
       The height of the board.
    n: int, default: 5
       The width of the board.
    k: int, default: 3
       The minimum number of marks a player has to place consecutively on the board to 
       win.
    -------------------------------------------------------------------------------------
    Returns: None
    -------------------------------------------------------------------------------------
    Example:
    mnkGame(m=10, 
             n=10,
             k=5)
    """
    _mnk(m,n,k).play_game()


