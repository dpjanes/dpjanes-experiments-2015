import sys
import re
import pprint

def load(file):
    ds = []

    fmt1_re = "^(space|pulse) (\d+)"
    fmt1_rex = re.compile(fmt1_re)

    fmt2_re = "^ *(\d+) +(\d+) +(\d+) +(\d+) +(\d+) +(\d+)"
    fmt2_rex = re.compile(fmt2_re)

    fin = open(sys.argv[1])
    while True:
        line = fin.readline()
        if not line:
            break

        fmt1_match = fmt1_rex.match(line)
        if fmt1_match:
            ds.append({
                "command": fmt1_match.group(1),
                "length": int(fmt1_match.group(2)),
            })
            continue

        fmt2_match = fmt2_rex.match(line)
        if fmt2_match:
            for x in xrange(0, 6):
                ds.append({
                    "command": x % 2 == 0 and "pulse" or "space",
                    "length": int(fmt2_match.group(x + 1)),
                })
            continue


    return ds

def trim(ds):
    while ds and ds[0]["command"] == "space":
        ds.pop(0)

    while ds and ds[-1]["command"] == "space":
        ds.pop(-1)

def by_command(ds, command):
    return filter(lambda d: d["command"] == command, ds)

def cluster(ds, variance=0.10):
    ## find clusters
    lts = []

    ## run twice in case averging perturbs values out
    for x in xrange(2):
        for d in ds:
            length = d["length"]
            length_m = length * ( 1 - variance )
            length_p = length * ( 1 + variance )

            found = False
            for lt in lts:
                if length_m < lt[0] and lt[0] < length_p:
                    lt[1].append(length)
                    lt[0] = sum(lt[1]) / len(lt[1])
                    found = True
                    break

            if not found:
                lts.append([ length, [ length, ]])

    ## assign to a cluster
    for d in ds:
        length = d["length"]
        length_m = length * ( 1 - variance )
        length_p = length * ( 1 + variance )

        for lt in lts:
            if length_m < lt[0] and lt[0] < length_p:
                d["cluster"]  = int(round(lt[0] / 10.0)) * 10
                break

    ## if no cluser, it gets it's own - rare
    for d in ds:
        if not d.get("cluster"):
            d["cluser"] = int(round(d["length"] / 10.0)) * 10

def onoffs(resultd):
    """Find 'raw_10s' and 'raw_times' and store in resultd
    
    raw_10s is guaranteed to be of even length
    """

    raw_deltas = set()
    raw_10s = []

    ## first find the raw_deltas
    for d in resultd["raw"]:
        raw_deltas.add(d["cluster"])

    raw_deltas = sorted(list(raw_deltas))

    ## the make a list of what each pulse goes to
    for d in resultd["raw"]:
        raw_10s.append("%x" % raw_deltas.index(d["cluster"]))

    ## make sure 10 is even length
    if len(raw_10s) % 2 == 1:
        raw_10s.append("0")

    resultd.update({
        "raw_times": raw_deltas,
        "raw_10s": "".join(raw_10s),
        "raw_10_chars": len(raw_10s) / 2,
    })

def bigrams(resultd):
    """Bigrams are common on-off combinations"""

    bi_10s = list(resultd["raw_10s"])
    raw_times = resultd["raw_times"]

    ## identify bigrams
    bigramd = {}
    for x in xrange(0, len(bi_10s) // 2 * 2, 2):
        bigram = bi_10s[x] + bi_10s[x + 1]
        bigramd[bigram] = bigramd.get(bigram, 0) + 1

    bigrams = bigramd.items()
    bigrams = filter(lambda b: b[1] > 1, bigrams)
    bigrams.sort(lambda a, b: cmp(b[1], a[1]))

    ## pprint.pprint(bigrams)
    ## sys.exit(0)

    ## only can have to 16 different lengths
    offset = len(raw_times)
    bigrams = bigrams[:16-offset];

    ## replace with bigrams and Nones
    for x in xrange(0, len(bi_10s) // 2 * 2, 2):
        bigram = bi_10s[x] + bi_10s[x + 1]
        for y in xrange(0, len(bigrams)):
            ## print bigrams[y]
            if bigrams[y][0] == bigram:
                bi_10s[x] = "%x" % ( y + offset )
                bi_10s[x + 1] = None

    ## filter out Nones
    bi_10s = filter(lambda oo: oo != None, bi_10s)

    ## make sure list is even length
    if len(bi_10s) % 2 == 1:
        bi_10s.append("0")

    ## the on/off times - orignal
    bi_10_times = []
    for time in raw_times:
        bi_10_times.append(( time, 0 ))

    ## the on/off times - from bigrams
    for bigram in bigrams[:16-offset]:
        bigram0 = int(bigram[0][0], 16)
        bigram1 = int(bigram[0][1], 16)

        bi_10_times.append(( raw_times[bigram0], raw_times[bigram1], ))

    ## the first part of the result
    resultd.update({
        "bi_10s": "".join(bi_10s),
        "bi_10_chars": len(bi_10s) / 2,
        "bi_10_times": bi_10_times,
    })

    ## now add the bi_10 times


    ## fo
    ## for t
    ## print lts
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >> sys.stderr, "usage: %s <data>.lirc" % sys.argv[0]
        sys.exit(1)

    resultd = {
        "raw": load(sys.argv[1])
    }

    trim(resultd["raw"])
    cluster(resultd["raw"])
    onoffs(resultd)
    bigrams(resultd)

    del resultd["raw"]
    pprint.pprint(resultd)
