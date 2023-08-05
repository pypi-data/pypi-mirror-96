import regex as re
import string
import os
import numpy as np

STOPWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
"you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves',
'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it',
"it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
'can', 'just',  'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y']

TOPICWORDS = ["no","not","nor",'ain', 'aren', "aren't", 'couldn', "couldn't",
'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
"mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
'wasn', "wasn't", 'weren', "weren't", 'won', "won't",'don', "don't",'wouldn',
"wouldn't", "\d+","\d+\.\d+", "will","reveal", "revealed", "h/o", "s/p","denies"
, "denied", "b.i.d.", "t.i.d.", "p.r.n.", "p.o.", "p.r.", "a.m.", "a.s.", "c.c.",
"n.p.o.", "o.d.", "o.s.", "o.u.", "q.s.", "q.o.d.","t.i.d.", "t.i.n."]

JOINERWORDS = [
"of",
"in",
"to",
"on",
"than",
"at"
]


def appendJoiners(merged, ranges, text, joinerwords):
    if len(joinerwords) == 0:
        return ranges
    joiners = "|".join(["(\s|^)"+stop+"(\s|$)" for stop in joinerwords])
    for i in range(len(merged)):
        match = merged[i]
        start = 0
        end = len(text)
        if not re.search("("+joiners+")", text[match[0]:match[1]]):
            continue
        if i > 0:
            start = merged[i-1][1]
        if i < len(merged)-1:
            end = merged[i+1][0]

        # must have text before and after it...
        if start != merged[i][0] and end != merged[i][1]:
            ranges.append((start,end, 'token'))
    return ranges

def mergeOverlappingTuples(matches):
    if len(matches) == 1:
        return matches
    prev = 0
    res = []
    for i in range(len(matches)-1):
        if matches[i][1] >  matches[i+1][0]:
            continue
        res.append((matches[prev][0], matches[i][1], 'noise'))
        prev = i+1
    if prev < len(matches):
        res.append((matches[prev][0], matches[-1][1], 'noise'))
    return res


def figureOutRegex(stopwords, topicwords, size=2):
    punc = [x for x in string.punctuation]
    regex = '\n|[\s' + "|\\".join(punc)+ ']{'+ str(size)+',}'

    topics = "|".join(["(\s|^)"+stop+"(\s|$)" for stop in topicwords])
    stops = "|".join(["(\s|^)"+stop+"(\s|$)" for stop in stopwords])

    if len(topics) != 0:
        regex = topics +"|" + regex
    if len(stops) != 0:
        regex = stops+'|'+regex

    regex = "("+regex+")"
    prog = re.compile(regex)
    return prog, topics


def appendMatches(matches, ranges, text):
    prev = 0
    for match in matches:
        if match[0]> prev:
            ranges.append((prev, match[0], 'token'))
        prev = match[1]
    if len(text) > prev:
        ranges.append((prev, len(text), 'token'))
    return ranges

def getRangesFromIter(matches):
    ranges = []
    for match in matches:
        ranges.append((match.start(), match.end(),'noise'))
    return ranges

def appendTopics(matches, ranges, text, topics):

    if len(topics) == 0:
        return ranges, matches
    matchret = []
    for match in matches:
        if re.match("("+topics+")", text[match[0]:match[1]]):
            start = match[0]
            end = match[1]
            if text[match[0]].isspace():
                start = start + 1
            if text[match[1]-1].isspace():
                end = end -1
            ranges.append((start, end, 'token'))
            continue
        matchret.append(match)
    return ranges, matchret

def assignParents(tokens):
    ranks = {}
    ranks["root"] = "root"
    ranks["\n"] = [":\n", "root"]
    ranks[":\n"] = ["\n", "root"]
    ranks[": "] = ["\n", ". ", ";"]
    ranks[". "] = ["\n"]
    ranks[","] = [";", ". ", "\n", "|", "-"]
    ranks[";"] = [". ", "\n"]
    ranks["-"] = [";", ". ", "\n", ",", "|"]
    ranks["|"] = [";", ". ", "\n", ",", "|"]
    ranks["and"] = [";", ". ", "\n", "|", "-"]
    ranks["or"] = [";", ". ", "\n", "|", "-"]
    ranks["by"] = [";", ". ", "\n", ",", "|", "-"]
    ranks["in"] = [";", ". ", "\n", ",", "|", "-"]
    ranks["on"] = [";", ". ", "\n", ",", "|", "-"]
    ranks["was"] = [";", ". ", "\n", ",", "|", "-"]
    ranks["is"] = [";", ". ", "\n", ",", "|", "-"]

    order = [":\n", "\n", ". ", ";", ": ", ",", "-", "and", "or", "|", "by", "in", "on", "was", "is"]

    lastKnown = {}
    lastKnown["root"] = -1
    lastKnown["\n"] = -1
    lastKnown[":\n"] = -1
    lastKnown[": "] = -1
    lastKnown[". "] = -1
    lastKnown[","] = -1
    lastKnown[";"] = -1
    lastKnown["-"] = -1
    lastKnown["and"] = -1
    lastKnown["or"] = -1
    lastKnown["|"] = -1
    lastKnown["by"] = -1
    lastKnown["in"] = -1
    lastKnown["on"] = -1
    lastKnown["was"] = -1
    lastKnown["is"] = -1
    prevNewLine = -1
    for i in range(len(tokens)):
        if tokens[i]["tokenType"] != "noise":
            prev = np.amax(np.array(list(lastKnown.values())))
            tokens[i]["parent"] = prev
            continue
        snip = tokens[i]["token"]
        done = False
        for ord in order:
            if ord in snip:
                prev = np.amax(np.array(list([lastKnown[r] for r in ranks[ord]])))
                tokens[i]["parent"] = prev
                lastKnown[ord] = i
                done = True
                break
        if done:
            continue
        prev = np.max(np.array(list(lastKnown.values())))
        tokens[i]["parent"] = prev
    return tokens

def wildgram(text, stopwords=STOPWORDS, topicwords=TOPICWORDS, include1gram=True, joinerwords=JOINERWORDS, returnNoise=True, includeParent=True):
    # corner case for inappropriate input
    if not isinstance(text, str):
        raise Exception("What you just gave wildgram isn't a string, mate.")
    if not returnNoise and includeParent:
        raise Exception("Parent is based on noise index, you need to set returnNoise to True in order to have includeParent be True. Otherwise set both to False.")

    if text.isspace() and not returnNoise:
        return []
    if text.isspace() and returnNoise:
        return [{"startIndex": 0, "endIndex":len(text), "token":text, "tokenType": "noise", "index": 0}]

    prog,topics = figureOutRegex(stopwords, topicwords)
    ranges = []
    matches = getRangesFromIter(prog.finditer(text.lower(),overlapped=True))
    ranges = appendMatches(matches, ranges, text)
    ranges, matches = appendTopics(matches, ranges, text, topics)
    merged = mergeOverlappingTuples(matches)
    ranges =appendJoiners(merged, ranges, text, joinerwords)

    noise = matches
    if include1gram:
        prog1gram,_ = figureOutRegex(stopwords,[], 1)
        matches = getRangesFromIter(prog1gram.finditer(text.lower(), overlapped=True))
        noise = noise + matches
        ranges = appendMatches(matches, ranges, text)
        merged = mergeOverlappingTuples(matches)
        ranges = appendJoiners(merged, ranges, text, joinerwords)

    if returnNoise:
        ranges = ranges + noise
    ranges =sorted(list(set(ranges)), key=lambda x: (x[0], x[1]))

    ret = []
    for r in ranges:
        app = {"startIndex": r[0], "endIndex": r[1], "token": text[r[0]:r[1]], "tokenType": r[2], "index": len(ret)}
        if len(ret) == 0:
            ret.append(app)
            continue
        if ret[-1]["tokenType"] != "noise":
            ret.append(app)
            continue
        if r[2] != "noise":
            ret.append(app)
            continue
        if ret[-1]["endIndex"] >= r[0]:
            if ret[-1]["endIndex"] < r[1]:
                ret[-1] = {"startIndex": ret[-1]["startIndex"], "endIndex": r[1], "token": text[ret[-1]["startIndex"]:r[1]], "tokenType": "noise", "index": len(ret)-1}
            continue
        ret.append(app)

    if includeParent:
        ret = assignParents(ret)

    return ret
