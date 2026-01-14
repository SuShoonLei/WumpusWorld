class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.kb = []   

    def inference_by_resolution(self, query):
        """
        Perform inference by resolution on the given query.
        """
        # Convert all KB sentences to CNF clauses
        clauses = [self.convert_to_cnf(s) for s in self.kb]
        # negate and convert 
        clauses.append(self.convert_to_cnf(self.negate(query)))

       
        clauses = {frozenset(self.flatten(c)) for c in clauses}

        new = set()
        while True:
            # all pairs of distinct clauses
            pairs = [(ci, cj) for ci in clauses for cj in clauses if ci != cj]

            for (ci, cj) in pairs:
                resolvents = self.resolve(ci, cj)
                if frozenset() in resolvents:  # empty clause = contradiction
                    return True
                new = new.union(resolvents)

            if new.issubset(clauses):
                return False

            clauses = clauses.union(new)

    def resolve(self, ci, cj):
        """
        Resolve two clauses in conjunctive normal form (CNF).
        """
        resolvents = set()
        for di in ci:
            for dj in cj:
                if dj == self.negate(di): 
                    new_clause = (ci - {di}) | (cj - {dj})
                    resolvents.add(frozenset(new_clause))
        return resolvents

    def negate(self, sentence):
        if isinstance(sentence, str):
            return ('NOT', sentence)
        elif isinstance(sentence, tuple) and sentence[0] == 'NOT':
            return sentence[1]
        else:
            return ('NOT', sentence)

    def convert_to_cnf(self, sentence):
        if isinstance(sentence, str):
            return [sentence]

        op = sentence[0]

        if op == 'IMPLIES':
            _, left, right = sentence
            return self.convert_to_cnf(('OR', ('NOT', left), right))

        elif op == 'IFF':
            _, left, right = sentence
            return self.convert_to_cnf(('AND',
                        ('OR', ('NOT', left), right),
                        ('OR', ('NOT', right), left)))

        elif op == 'AND':
            _, left, right = sentence
            return self.convert_to_cnf(left) + self.convert_to_cnf(right)

        elif op == 'OR':
            _, left, right = sentence
            return [self.flatten(self.convert_to_cnf(left) + self.convert_to_cnf(right))]

        elif op == 'NOT':
            _, inner = sentence
            if isinstance(inner, tuple) and inner[0] == 'NOT':
                return self.convert_to_cnf(inner[1]) 
            else:
                return [sentence]

        else:
            return [sentence]

    def flatten(self, cnf):
       
        if isinstance(cnf, str) or (isinstance(cnf, tuple) and cnf[0] == 'NOT'):
            return [cnf]
        new_cnf = []
        for x in cnf:
            if isinstance(x, list):
                new_cnf.extend(self.flatten(x))
            else:
                new_cnf.append(x)
        return new_cnf


# --- Starter main function for testing ---
if __name__ == "__main__":
    player = Player()

    # Test 1: KB = ['P', ('IMPLIES', 'P', 'Q')]
    player.kb = ['P', ('IMPLIES', 'P', 'Q')]
    print("Test 1 - Q:", player.inference_by_resolution('Q'))  # Expected: True
    print("Test 1 - NOT Q:", player.inference_by_resolution(('NOT', 'Q')))  # Expected: False

    # Test 2: KB = [('NOT', 'B11'), ('IFF', 'B11', ('OR', 'P12', 'P21'))]
    player.kb = [('NOT', 'B11'), ('IFF', 'B11', ('OR', 'P12', 'P21'))]
    print("Test 2 - P21:", player.inference_by_resolution('P21'))  # Expected: False
