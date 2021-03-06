#!/usr/bin/env python

import csv
import requests
from StringIO import StringIO
import pysolr
import os
import zipfile
import io
import time
import socket
import dns.resolver

POSTCODE_ZIP="https://www.freemaptools.com/download/full-postcodes/ukpostcodes.zip"

FIELD_NAMES=["id", 
             "price_i", 
	     "transaction_date_dt", 
	     "postcode_s", 
	     "property_type_s", 
	     "age_s", 
	     "duration_s", 
	     "paon_t", 
	     "saon_t", 
	     "street_t", 
	     "locality_t",
	     "town_t",
	     "district_t",
	     "county_t",
	     "ppd_s",
	     "status_s"]

FIELD_FORMATS={"transaction_date_dt": "date",
               "postcode_s": "geo"}

BATCH_SIZE=1000

#"{34428D7D-BD85-B86C-E050-A8C06205059C}","275000","2004-04-01 00:00","RG12 7BD","D","N","F","CALCOT HOUSE","","RECTORY CLOSE","","BRACKNELL","BRACKNELL FOREST","BRACKNELL FOREST","A","A"

def download_postcodes(url="https://www.freemaptools.com/download/full-postcodes/ukpostcodes.zip"):
  print "Downloading postcodes..."
  resp = requests.get(url)
  f = io.BytesIO(resp.content)
  z = zipfile.ZipFile(f)
  print "Unzipping..."
  data = z.read("ukpostcodes.csv")

  print "Extracting..."
  postcodes = {}
  for line in data.split("\n")[1:]:
    if len(line.strip())>0:
      id, postcode, lat, lng = line.strip().split(",")
      postcodes[postcode] = "%s,%s" % (lat, lng)
  print "Found %d postcodes" % len(postcodes.keys())
  return postcodes


def readlines(url):
    print "Requesting %s" % url
    r = requests.get(url, stream=True, allow_redirects=True)
    print r.history
    print "Request sent. Processing stream"
    previous = ""
    i=0
    for chunk in r.iter_content(chunk_size=512 * 1024): 
      if chunk:
        lines = chunk.split("\n")
        if len(lines)>0:
          lines[0] = previous + lines[0]
          previous = lines[-1]
          for line in lines[:-1]:
            yield line


def import_houses(postcodes, solr, file="pp-monthly-update-new-version.csv"):
  url = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv"
  url = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"
  url = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-2016.csv"

  cnt=0
  docs=[]
  for line in readlines(url):
    r = csv.reader(StringIO(line))
    row = r.next()
    cnt+=1
    doc = {}
    i=0
    for field in row:
      field_name = FIELD_NAMES[i]
      format = FIELD_FORMATS.get(field_name, "none")
      if format == "none":
        doc[field_name] = field
      elif format == "date":
        date = field.replace(" ", "T") + ":00Z"
        doc[field_name] = date
      elif format == "geo":
        doc[field_name] = field.replace(" ", "_")
        latlon = postcodes.get(field, None)
        if latlon:
          doc["location"] = latlon
      else:
        print "UKNOWN FORMAT: %s" % format
      i+=1
    docs.append(doc)

    if len(docs)>=BATCH_SIZE:
        while True:
            try:
                solr.add(docs)
                break
            except Exception, e:
                print "Exception indexing documents: %s" % e
                time.sleep(5000)

        print "Imported %s prices. Total %s" % (len(docs), cnt)
        docs=[]

  if len(docs)>0:
    solr.add(docs)

  return cnt

def resolve_zookeeper_string():
    zk_host = os.environ.get("ZOOKEEPER", "zookeeper")
    zk_port = os.environ.get("ZK_PORT", "2181")
    zk_chroot = os.environ.get("ZK_CHROOT", "/solr")

    if "," in zk_host:
        return ",".join(["%s:%s" % (ip, zk_port) for ip in zk_host.split(",")]) + zk_chroot
    try:
        addresses = [str(name) for name in dns.resolver.query(zk_host, "A")]
    except:
        addresses = []
    if len(addresses)<2:
        return "%s:%s%s" % (zk_host, zk_port, zk_chroot)
    else:
        addresses = ["%s:%s" % (ip, zk_port) for ip in addresses]
        return ",".join(addresses) + zk_chroot


def get_zookeeper_hosts():
    zookeeper = os.environ.get("ZOOKEEPER", "zookeeper")

    zk_hosts = []
    if "," in zookeeper:
      zk_hosts = zookeeper.split(",")
    else:
        try:
            names = dns.resolver.query(zookeeper, "A")
            for name in names:
                zk_hosts.append(str(name))
        except:
            pass # do nothing
            zk_hosts = []
        if len(zk_hosts)==0:
            zk_hosts = [zookeeper]

    return zk_hosts


def get_zookeeper_status(zk_host, zk_port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    try:
        print "Connecting to %s:%s" % (zk_host, zk_port)
        s.connect((zk_host, zk_port))

        s.sendall("srvr\n")
        data = s.recv(4096)
        lines = repr(data).split("\\n")
        for line in lines:
            if line.startswith("Mode:"):
                mode = line[len("Mode: "):]
                s.close()
                return mode
    except Exception, e:
        print "Caught exception: %s" % e
        return "missing"

    print "Zookeeper not found."
    return "missing"


def wait_for_quorum():
    zk_port = int(os.getenv("ZK_PORT", "2181"))
    zk_hosts = get_zookeeper_hosts()
    print "Checking %s" % zk_hosts
    is_single = len(zk_hosts) == 1;
    while True:
      if is_single:
          zk_host = zk_hosts[0]
          if get_zookeeper_status(zk_host, zk_port) == "standalone":
              return
          else:
              print "Waiting for single host to start"
      else:
        active_count = 0;
        for zk_host in zk_hosts:
          status = get_zookeeper_status(zk_host, zk_port);
          if status == "leader" or status == "observer" or status == "follower":
            active_count+=1;

        if active_count == len(zk_hosts):
            print "All %s ZooKeeper hosts active" % len(zk_hosts)
            return
        else:
          print "%s out of %s ZooKeeper hosts active. Waiting" % (active_count, len(zk_hosts))
      time.sleep(5)


def index():
  wait_for_quorum()
  print "Importing postcodes"
  pc = download_postcodes()
  print "Imported %s postcodes" % len(pc.keys())


  zk = resolve_zookeeper_string()
  print "USING %s" % zk
  while True:
    try:
      solr = pysolr.SolrCloud(pysolr.ZooKeeper(zk), "houseprices")
      break
    except Exception, e:
      print "Solr connection failed, waiting: %s" % e
      time.sleep(5)

  count = import_houses(pc, solr)
  print "%s prices imported" % count
