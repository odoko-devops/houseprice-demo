#!/usr/bin/env python

import os
import sys
import indexer
import webapp

def main():
  if len(sys.argv)!=2:
    print "Choose index or run"
    sys.exit(1)

  action = sys.argv[1]
  if action == "index":
    indexer.index()
  elif action == "run":
    webapp.run()
  elif action == "test":
    os.system("behave")
  else:
    print "Unknown action: %s, choose from index or run" % action

if __name__ == "__main__":
  main()
