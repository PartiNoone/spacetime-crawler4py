import sys


def isAlphaNumeric(char:str):
    '''
    Helper function for core function tokenize:

    Time complexity:
    Constant time-- O(1)

    Reasoning: 
    There is worst-case scenario 9 operations: six <= operators,
    two "or" operators, and one return statement.
    '''
    # Only takes in single characters as input
    if 'A' <= char <= 'Z' or 'a' <= char <= 'z' or '0' <= char <= '9':
        return True
    return False


def tokenize_string(line:str):
    """
    Helper function for core function tokenize:

    Time complexity:
    Linear time-- O(n), where n is the number of characters in the line.

    Reasoning:
    There is one for-loop that iterates through each character
    in the line. All operations inside the for-loop take O(1) time.
    """
    line = line + ' ' # final whitespace to ensure the last token is not missed
    tokens = []
    str_len = len(line)
    start, end = (-1, -1)
    for i in range(0, str_len): # iterate over each char
        char = line[i]
        if isAlphaNumeric(char): # alphanumeric as in ONLY letters and numbers, nothing else
            if start == -1:
                start, end = (i, i + 1)
            else:
                end = i + 1
        else:
            if start < end:
                # if there is a token, add it to list and reset start and end
                tokens.append(line[start:end])
                start, end = (-1, -1)
    return tokens


def tokenize(filepath:str):
    """
    Tokenize:

    Time complexity:
    Linear time-- O(n), where n is the number of characters in the file.
    If n is the number of tokens in the file, it is still O(n).

    Reasoning:
    Essentially, this function iterates through every character in the file,
    so its time complexity is O of (number of lines) * (number of characters in a
    line), or simply O(number of characters in file).

    For n = number of tokens: Let us define a constant M
    that represents the average number of characters in a token. Now,
    the total number of characters C is equal to the number of tokens
    multiplied by the number of characters per token: C = Mn. M is a constant,
    so the equation allows us to write O(Mn) as simply O(n).
    """
    # return [-1] if error
    if len(filepath) == 0:
        print("Error in function tokenize: No file path provided")
        return [-1]
    tokens = []
    try:
        with open(filepath, 'r') as file: # what to do if input path is invalid...
            for line in file:
                tokens += tokenize_string(line.lower())
        return tokens
    except OSError:
        print("Error in function tokenize: File cannot be opened")
        return [-1]


def computeWordFrequencies(token_list:list):
    """
    computeWordFrequencies:

    Time complexity:
    Quadratic time-- O(n^2), where n is the number of tokens in the input list

    Reasoning:
    There is one for-loop that iterates through every token in
    token_list. The "in" operator for token_list is located
    inside the for-loop and takes O(n), which means the whole
    function is O(n^2).
    """
    if len(token_list) == 0 or token_list[0] == -1:
        print("Error in function computeWordFrequencies: No tokens provided")
        return {}
    token_map = {}
    for token in token_list:
        if token in token_map:
            token_map[token] += 1
        else:
            token_map[token] = 1
    return token_map


def printFrequencies(token_dict:dict[str:int]):
    """
    printFrequencies:

    Time complexity:
    Linear Log time-- O(nlogn), where n is the number of token-frequency
    pairs in the input dict. Log is log base 2. 

    Reasoning:
    Initializing the freq_list variable uses items() and list() functions,
    which are O(n). Calling sorted() will take O(nlogn), like many
    sorting algorithms. Calling reverse() will take O(n). Then there is
    one for-loop that iterates through every token-frequency
    pair in the input dict, which is an additional O(n). O(nlogn) is
    the most significant, so the others are not counted.
    """
    if len(token_dict) == 0:
        print("Error in function printFrequencies: No map provided")
        return
    freq_list = list(token_dict.items())
    freq_list = sorted(freq_list, key= lambda tuple: tuple[1])
    freq_list.reverse()
    for item in freq_list:
        print(f"{item[0]}\t{item[1]}")


def runPartA():
    """
    Helper function to run all of Part A:

    Time complexity:
    Quadratic time-- O(n^2), where n is the number of tokens
    in the file. 

    Reasoning:
    This calls tokenize(), which is O(n), followed by
    computeWordFrequencies(), which is O(n^2), and finally
    printFrequencies(), which is O(nlogn).
    O(n) + O(n^2) + O(nlogn) = O(n^2)
    """
    if len(sys.argv) < 2:
        print("Error: No file path found")
        return

    token_list = tokenize(sys.argv[1])
    token_list_len = len(token_list)
    if token_list_len == 0:
        print("No tokens found.")
        return
    elif token_list[0] == -1:
        print("Error: Invalid file path given")
        return

    freq_dict = computeWordFrequencies(token_list)
    printFrequencies(freq_dict)


if __name__ == "__main__":
    runPartA()