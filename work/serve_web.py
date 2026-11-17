from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json,threading
from build_web import build, ROOT

lock=threading.Lock()
paths=[ROOT/'work'/p for p in ['editable-deck.svg','deck.json','viewer.html']]
build()
stamp=tuple(p.stat().st_mtime_ns for p in paths)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'outputs'),**kwargs)
    def do_GET(self):
        global stamp
        if urlparse(self.path).path=='/api/revision':
            with lock:
                now=tuple(p.stat().st_mtime_ns for p in paths)
                if now!=stamp:
                    build()
                    stamp=now
                data=json.dumps({'revision':str(stamp)}).encode()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers();self.wfile.write(data)
        else:
            if urlparse(self.path).path=='/': self.path='/Qualifying%20Exam.html'
            super().do_GET()
    def log_message(self,*args): pass

print('Live slides: http://127.0.0.1:8765',flush=True)
ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
