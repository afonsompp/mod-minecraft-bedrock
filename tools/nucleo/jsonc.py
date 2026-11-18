import json, re, sys
def load(path):
    s = open(path, encoding='utf-8').read()
    out, i, n, ins = [], 0, len(s), False
    while i < n:
        c = s[i]
        if ins:
            out.append(c)
            if c == '\\': out.append(s[i+1]); i += 2; continue
            if c == '"': ins = False
            i += 1; continue
        if c == '"': ins = True; out.append(c); i += 1; continue
        if s.startswith('//', i):
            j = s.find('\n', i); i = n if j < 0 else j; continue
        if s.startswith('/*', i):
            j = s.find('*/', i); i = n if j < 0 else j + 2; continue
        out.append(c); i += 1
    t = re.sub(r',(\s*[}\]])', r'\1', ''.join(out))
    return json.loads(t)
