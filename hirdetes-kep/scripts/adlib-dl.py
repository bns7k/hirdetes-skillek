# -*- coding: utf-8 -*-
"""Meta Hirdetestar-kreativok letoltese egy 'nev<TAB>url' fajlbol.

Az URL-eket a bongeszobol szeded ki (lasd references/referencia-kutatas.md),
mert az fbcdn-linkek alairtak es lejarnak.

    python adlib-dl.py batch.txt

A fajl minden sora:  nev<TAB>https://scontent...
"""
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def main():
    src = sys.argv[1]
    ok = 0
    for line in open(src, encoding="utf-8"):
        if "\t" not in line:
            continue
        name, url = line.rstrip("\n").split("\t", 1)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) < 2000:
                raise ValueError("tul kicsi: %d B" % len(data))
            with open(name + ".jpg", "wb") as f:
                f.write(data)
            print("OK   %-22s %7d B" % (name, len(data)))
            ok += 1
        except Exception as e:
            print("HIBA %-22s %s" % (name, e))
    print("%d letoltve" % ok)


if __name__ == "__main__":
    main()
