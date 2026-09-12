"""Follow the form action actually returned by IMD; do not guess data paths."""
from probe_sources import probe, RAW
import re
import urllib.parse
import json
page=(RAW/'imd.txt').read_text(encoding='utf8')
action=re.search(r'<form[^>]*name="RF25"[^>]*action="([^"]+)"',page).group(1)
url=urllib.parse.urljoin('https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html',action)
result=probe(('imd_download',(url,urllib.parse.urlencode({'RF25':'2013'}).encode())))
(RAW/'imd-download-probe.json').write_text(json.dumps(result,indent=2))
print(result)
