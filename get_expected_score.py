import sys

def get_expected_scores(ra,rb):
    """Return E_a and E_b from https://en.wikipedia.org/wiki/Elo_rating_system#Theory"""
    qa = 10**(ra/400)
    qb = 10**(rb/400)
    ea = qa/(qa + qb)
    eb = qb/(qa + qb)
    return ea, eb

def get_expected_scores(*largs):
    qs = [10**(l/400) for l in largs]
    agg_q = sum(qs)
    es = [q/agg_q for q in qs]
    return es

if __name__=='__main__':
    rs = [int(arg) for arg in sys.argv[1:]]
    es = get_expected_scores(*rs)
    for i, e in enumerate(es):
        print('E_%d: %f' % (i, e))