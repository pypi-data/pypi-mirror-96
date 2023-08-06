import numpy as np
from itertools import product

class operator:
    m = [ np.array([[1,0],[0,1]]), np.array([[0,1],[0,0]]), np.array([[0,0],[1,0]]), np.array([[0,0],[0,1]]) ]

    def __init__(self, terms=None):
        if( terms == None ):
            self.terms = {}
        else: self.terms = terms

    def _conj(self, term):
        def _local_conj(c):
            if c == "1": return "2"
            elif c == "2": return "1"
            else: return c

        newString = list(map(_local_conj, term))
        return "".join(newString)

    def expand(term, coeff):
        if( term == None ):
            return {}

        # Recursive call
        if "5" not in term:
            return {term:coeff}

        # {'505':3}
        # {'005':3, '305':-1}

        expanded_terms = {}
        for i in range(len(term)):
            if term[i] == "5":
                newString1 = term[:i] + "0" + term[i + 1:]
                newString2 = term[:i] + "3" + term[i + 1:]

                expanded_terms.update( operator.expand(newString1, coeff*1) )
                expanded_terms.update( operator.expand(newString2, coeff*-1) )

                # We recursively expand every 5, so once we've found one, we can leave here
                break

        return expanded_terms

    def conj(self):
        newOperator = operator({})
        newOperator.terms = {self._conj(k): np.conjugate(v) for k, v in self.terms.items()}
        return newOperator

    def cleanup(self, threshold=1e-8):
        newOperator = operator({})
        newOperator.terms = {k:v for k, v in self.terms.items() if np.abs(v) >= threshold}
        return newOperator

    def isDiagonal(self):
        for term in self.terms:
            if( "1" in term or "2" in term ):
                return False
        return True

    def _toMatrix(self, term):
        if( len(term) < 2 and len(term) != 0 ):
            return operator.m[int(term[0])]

        matrix = np.kron( operator.m[int(term[0])], operator.m[int(term[1])] )
        for c in term[2:]:
            matrix = np.kron(matrix, operator.m[int(c)])
        return matrix

    def toMatrix(self):
        '''
        Return this operator as a dense matrix
        '''
        matrix = 0
        for term in self.terms:
            matrix += self.terms[term] * self._toMatrix(term)
        return matrix

    def __add__(self, other):
        # Add two operators
        newOperator = operator({})
        newOperator.terms = self.terms

        for term in other.terms:
            newOperator.terms[term] = newOperator.terms.get(term,0) + other.terms[term]

        return newOperator.cleanup()

    def __sub__(self, other):
       # Subtract two operators
        newOperator = operator({})
        newOperator.terms = self.terms

        for term in other.terms:
            newOperator.terms[term] = newOperator.terms.get(term,0) - other.terms[term]

        return newOperator.cleanup()

    def _multiply(self, c1, c2):
        newString = None
        newCoeff = 1

        # Take care of the identity
        if c1 == "0":
            newString = c2
        elif c2 == "0":
            newString = c1

        # If the first is a sx
        elif c1 == "1":
            # If c2 is also a sx
            if c2 == "1":
                newString = "0"

            # If c2 is a sy
            if c2 == "2":
                newString = "3"  # sx*sy == i*sz
                newCoeff *= 1j

            if c2 == "3":  # sx*sz = -i*sy
                newString = "2"
                newCoeff *= -1j

        # If the first is a sy
        elif c1 == "2":
            # If c2 is a sx
            if c2 == "1":
                newString = "3"
                newCoeff *= -1j

            if c2 == "2":
                newString = "0"

            if c2 == "3": #sy*sz = i*sx
                newString = "1"
                newCoeff *= 1j

        # If the first is a sz
        elif c1 == "3":
            # If c2 is a sx
            if c2 == "1":
                newString = "2"
                newCoeff *= 1j

            if c2 == "2":
                newString = "1"
                newCoeff *= -1j

            if c2 == "3":
                newString = "0"

        return (newString, newCoeff)

    def _mul(self, terms):
        term1, term2 = terms[0], terms[1]
        newTerm = list( map(self._multiply, term1[0], term2[0]) )
        newString = [i[0] for i in newTerm]
        newval = term1[1] * term2[1] * np.prod([i[1] for i in newTerm])

        if None in newString:
            return [(None, newval)]

        if "5" not in newString:
            return [("".join(newString), newval)]
        else:
            expanded_terms = operator.expand("".join(newString), newval)
            return [(k,v) for (k,v) in expanded_terms.items()]

    def __mul__(self, other):
        newOperator = operator({})

        if(type(other) in (int, float, complex)):
            newOperator.terms = {k:v*other for k, v in self.terms.items()}
        else:
            allcombos = list(product( self.terms.items(), other.terms.items() ))
            allterms = map(self._mul, allcombos)
            flatterms = [item for sublist in allterms for item in sublist if item[0] != None]

            # TODO: Get rid of this for loop!
            for term in flatterms:
                newOperator.terms[term[0]] = newOperator.terms.get(term[0],0) + term[1]
            #newOperator.terms = {k:newOperator.terms.get(k,0)+v for (k, v) in flatterms}
            return newOperator.cleanup()

        return newOperator.cleanup()

    def __rmul__(self, other):
        newOperator = operator({})
        if(type(other) in (int, float, complex)):
            newOperator.terms = {k:v*other for k, v in self.terms.items()}
        else:  # We're multiplying other * operator
            # Always perform multiplication with left term first
            return other.__mul__(self)
        return newOperator.cleanup()

    def __str__(self):
        if(len(self.terms.items()) == 0):
            return "None"

        string = ""
        for i, term in enumerate(self.terms):
            string += "Term {0}: {1} {2}\n".format(i, term, self.terms[term])
        return string
