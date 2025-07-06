import os, requests as req
import vision2 as vision
from store.bucket import Bucket

import uuid
USAGE = "Please upload a picture and I will tell you what I see"
FORM = [
  {
    "label": "Load Image",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]
s3 = Bucket()
def form(args):
  res = {}
  out = USAGE
  inp = args.get("input", "")

  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    print(f"uploaded size {len(img)}")
    #storing to s3
    myuuid = uuid.uuid4()
    import datetime;
    ct = datetime.datetime.now()
    name = str(myuuid) + "_" + str(ct)
    vis = vision.Vision(args)
    out = vis.decode(img)
    s3.write(name, out)
    res['html'] = f'<img src="data:image/png;base64,{img}">'
    
  res['form'] = FORM
  res['output'] = out
  return res
