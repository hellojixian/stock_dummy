#
#
# def solution(S):
#     # write your code in Python 2.7
#     stack = []
#     digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
#     ops = ['+', '*']
#     for i in range(len(S)):
#         char = S[i]
#         if char in digits:
#             stack.append(int(char))
#         elif char in ops:
#             # check stack has enough elements
#             if len(stack) < 2:
#                 return -1
#             elems = stack[-2:]
#             if char == '+':
#                 new_value = elems[0]+elems[1]
#             elif char == '*':
#                 new_value = elems[0]*elems[1]
#             stack = stack[:-2]
#             stack.append(new_value)
#         else:
#             return -1
#     return stack[-1]
#
#
# print(solution('13+62*7+*'))

def solution(A):
    # write your code in Python 2.7
    # first need to parse the string into RGB list
    R, G, B = [], [], []
    for i in range(0, len(A), 3):
        R.append(A[i])
        if i + 1 < len(A):
            G.append(A[i + 1])
        if i + 2 < len(A):
            B.append(A[i + 2])

    print(R, G, B)
    magics = []

    # find out all possible magic sum numbers
    for r in range(len(R)):
        n = R[r]
        if n not in magics:
            magics.append(n)
        for b in range(len(B)):
            n = R[r] + B[b]
            if n not in magics:
                magics.append(n)
    for g in range(len(G)):
        n = G[g]
        if n not in magics:
            magics.append(n)
        for b in range(len(B)):
            n = G[g] + B[b]
            if n not in magics:
                magics.append(n)
    for g in range(len(G)):
        n = G[g]
        if n not in magics:
            magics.append(n)
        for r in range(len(R)):
            n = G[g] + R[r]
            if n not in magics:
                magics.append(n)

    print(magics)
    # check them one by one
    for m_i in range(len(magics)):
        m = magics[m_i]
        result = []
        # is it possible the i pos to R
        for i in range(len(A)):
            for r in range(len(R)):
                if R[r] == m :
                    result.append('R')
                for g in range(len(G)):
                    if R[r] + G[g] == m:
                        result.append('G')
                for b in range(len(B)):
                    if R[r] + B[b] == m:
                        result.append('B')
    print("".join(result))
    if len(result) == len(A):
        return "".join(result)

    return 'impossible'


print(solution([3, 7, 2, 5, 4]))
