import PartA as A
import sys


def findIntersection(list1: list, list2: list):
    """
    Function to find the intersection of two lists:

    Time complexity:
    Linear Log time-- O(nlogn), where n is the number of tokens
    in the file. 

    Reasoning:
    This calls sort(), which is O(nlogn). Then it
    calls len(), which is O(1). The while loop iterates
    through each token, so it is O(n). Of these, O(nlogn)
    is the most significant, so we take that.
    """
    list1.sort()
    list2.sort()
    result = []
    pointer1 = 0
    pointer2 = 0
    len1 = len(list1)
    len2 = len(list2)
    while pointer1 < len1 and pointer2 < len2:
        if list1[pointer1] < list2[pointer2]:
            pointer1 += 1
        elif list2[pointer2] < list1[pointer1]:
            pointer2 += 1
        else:
            result.append(list1[pointer1])
            pointer1 += 1
            pointer2 += 1
    print(result)
    print(len(result))
    return result

def runPartB():
    """
    Time Complexity: O(nlogn)
    Reasoning: findIntersection() takes O(nlogn) time, and there
    are no loops in this function (other than in findIntersection).
    """
    if len(sys.argv) < 3:
        print("Error: Program requires two files to find intersection")
        return
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    tokenlist1 = A.tokenize(filename1)
    tokenlist2 = A.tokenize(filename2)
    if len(tokenlist1) == 0 or len(tokenlist2) == 0:
        print(0)
        return
    elif tokenlist1[0] == -1 or tokenlist2[0] == -1:
        print("Error: Invalid file path(s) given")
        return
    findIntersection(tokenlist1, tokenlist2)

if __name__ == "__main__":
    runPartB()