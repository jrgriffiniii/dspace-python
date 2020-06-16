'''
   This Python script can be used to bind a set of ARKs to the URL of the
   corresponding item in DSpace.

   The ARK identifiers are read from a file = arkfile

   Author:  Mark Ratliff
'''

import requests

arkfile = "list_of_arks.txt"

f = open(arkfile,"r") #opens file with name of "test.txt"

for ark in f:
  # Strip the newline off the end of the ARK
  ark = ark.rstrip('\n')

  # Build the URL that the ARK server will redirect to
  dspace_url = "http://dataspace.princeton.edu/handle/" + ark

  # Build the URL that will be used to bind the ARK to the redirect URL
  ark_bind_url = "http://arks.princeton.edu/nd/noidu_scratch?bind+set+" + ark + "+location+" + dspace_url
  print "ARK binding URL:  " + ark_bind_url

  ark_resolve_url = "http://arks.princeton.edu/ark:/" + ark

  # Send request to the ARK server
  r = requests.get(ark_resolve_url, allow_redirects=False)

  print r.status_code
  print '\n'
  print r.headers
  print '\n'
  print r.content

f.close();
