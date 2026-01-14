def parse_literal(lit):
    """Parse a literal string into (sign, term)."""
    s = lit.strip()
    if not s:
        return True, s
    if s[0] in ('¬', '~', '!'):
        return False, s[1:].strip()
    if s.lower().startswith('not '):
        return False, s[4:].strip()
    return True, s

def negate_literal(lit):
    """Return negation of literal string."""
    sign, term = parse_literal(lit)
    if sign:
        return "¬" + term
    else:
        return term

def substitute_literal(lit, subs):
    """Apply substitutions to the inner term of a literal and return new literal string."""
    sign, term = parse_literal(lit)
    new_term = apply_subs(term, subs)
    return (new_term if sign else "¬" + new_term)

def is_tautology(clause):
    """True if clause contains a literal and its negation (after normalization)."""
    lits = set(clause)
    for l in lits:
        if negate_literal(l) in lits:
            return True
    return False


def parse_predicate(sentence):
    """Split a FOL sentence into predicate name and argument list."""
    name, args = sentence.split('(', 1)
    name = name.strip()
    args = args[:-1]  # remove the closing parenthesis
    args = [a.strip() for a in args.split(',')] # split arguments by comma
    return name, args


def is_variable(token):
    """Check if a token is a variable (starts with lowercase and alphabetic)."""
    return token.isalpha() and token[0].islower()


def apply_subs(term, result):
    """Recursively apply substitutions to a term."""
    while term in result:
        term = result[term] 

    if '(' in term and term.endswith(')'):
        name, args = parse_predicate(term)
        new_args = [apply_subs(a, result) for a in args] 
        return f"{name}({', '.join(new_args)})"
    return term

def occurs(var, term, result):
    """Check if var occurs inside term (to prevent infinite substitution)."""
    term = apply_subs(term, result)
    if var == term:
        return True
    if '(' in term and term.endswith(')'):
        _, args = parse_predicate(term)
        return any(occurs(var, a, result) for a in args)
    return False


def unify(x, y, result):
    """Unify two FOL terms and update substitution map."""
    x = apply_subs(x, result)
    y = apply_subs(y, result)

    # identical terms
    if x == y:
        return True

    # variable unification
    if is_variable(x):
        if occurs(x, y, result):
            return False
        result[x] = y
        return True

    if is_variable(y):
        if occurs(y, x, result):
            return False
        result[y] = x
        return True

    # function or predicate unification
    if '(' in x and '(' in y:
        name1, args1 = parse_predicate(x)
        name2, args2 = parse_predicate(y)
        if name1 != name2 or len(args1) != len(args2):
            return False
        for a1, a2 in zip(args1, args2):
            if not unify(a1, a2, result):
                return False
        return True

    return False


def are_identical(sentence1, sentence2):
    """Check if two FOL sentences can be unified."""
    name1, args1 = parse_predicate(sentence1)
    name2, args2 = parse_predicate(sentence2)

    if name1 != name2 or len(args1) != len(args2):
        return False, {}

    result = {}
    for a1, a2 in zip(args1, args2):
        if not unify(a1, a2, result):
            return False, {}
    return True, result

#Part 2

def resolve_clause(clause1, clause2):
    """Resolve two clauses and return the resolvent clauses."""
    resolvents = []
    for l1 in list(clause1):
        sign1, term1 = parse_literal(l1)
        for l2 in list(clause2):
            sign2, term2 = parse_literal(l2)
            # Check if they are complementary
            if sign1 != sign2:
                subs = {}
                if unify(term1, term2, subs):
                    new_clause = set()
                    for lit in clause1.union(clause2):
                        if lit != l1 and lit != l2:
                            new_clause.add(substitute_literal(lit, subs))
                    if not is_tautology(new_clause):
                        resolvents.append(new_clause)
    return resolvents


def inference_by_resolution(kb, query):
    """Determine if the knowledge base entails the query using resolution."""
    # Negate the query and add to KB
    negated_query = negate_literal(query)
    clauses = [set(c if isinstance(c, list) else [c]) for c in kb]
    clauses.append(set([negated_query]))

    new = []
    while True:
        pairs = [(clauses[i], clauses[j]) for i in range(len(clauses)) for j in range(i + 1, len(clauses))]
        new_clauses = []
        for (ci, cj) in pairs:
            resolvents = resolve_clause(ci, cj)
            for r in resolvents:
                if not r:
                    return True  # Empty clause found ⇒ query is entailed
                if r not in clauses and r not in new_clauses:
                    new_clauses.append(r)
        if not new_clauses:
            return False  # No new clauses ⇒ cannot prove query
        for c in new_clauses:
            clauses.append(c)


# Test Cases for part 1
examples = [
    ("Parent(x, y)", "Parent(John, Mary)"),
    ("Loves(father(x), x)", "Loves(father(John), John)"),
    ("Loves(father(x), x)", "Loves(father(John), Mary)")
]

for s1, s2 in examples:
    identical, result = are_identical(s1, s2)
    print(f"{s1}  <->  {s2}")
    print("Result:", result)


#  Test Case for part 2
kb = [
    ["¬King(x)", "¬Greedy(x)", "Evil(x)"],
    ["King(John)"],
    ["Greedy(John)"]
]
query = "Evil(John)"

result = inference_by_resolution(kb, query)
print("KB:", kb)
print("Q: ", query)
print("Result: ", result)
