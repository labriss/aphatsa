"""Lit quelques fichiers dans l'archive SIWIS distante sans la télécharger (requêtes HTTP partielles).
python zipdistant.py liste [motif] | python zipdistant.py extraire <dossier> <nom> [<nom> ...]"""
import io, sys, urllib.request, zipfile
URL = "https://datashare.ed.ac.uk/server/api/core/bitstreams/64de089d-0ad5-45cb-a1c0-b6b39ecf6225/content"
class Distant(io.RawIOBase):
    def __init__(s):
        s.p = 0; s.n = int(urllib.request.urlopen(urllib.request.Request(URL, headers={"Range": "bytes=0-0"})).headers["Content-Range"].split("/")[1])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.p
    def seek(s, o, w=0):
        s.p = o if w == 0 else s.p + o if w == 1 else s.n + o; return s.p
    def read(s, k=-1):
        if k < 0: k = s.n - s.p
        if k == 0 or s.p >= s.n: return b""
        r = urllib.request.urlopen(urllib.request.Request(URL, headers={"Range": f"bytes={s.p}-{min(s.n, s.p + k) - 1}"})).read()
        s.p += len(r); return r
    def readinto(s, b):
        d = s.read(len(b)); b[:len(d)] = d; return len(d)
z = zipfile.ZipFile(io.BufferedReader(Distant(), 1 << 20))
if sys.argv[1] == "liste":
    for i in z.infolist():
        if len(sys.argv) < 3 or sys.argv[2] in i.filename: print(i.filename, i.file_size)
else:
    for nom in sys.argv[3:]: z.extract(nom, sys.argv[2]); print("ok", nom)
