import os
from flask import Flask, request, send_from_directory, jsonify
import pysolr

app = Flask(__name__)

FIELD_NAMES={
         "id": "id",
         "price_i": "price",
	     "transaction_date_dt": "date",
	     "postcode_s": "postcode",
	     "property_type_s": "type",
	     "age_s": "age",
	     "duration_s": "duration",
	     "paon_t": "number",
	     "saon_t": "name",
	     "street_t": "street",
	     "locality_t": "locality",
	     "town_t": "town",
	     "district_t": "district",
	     "county_t": "county",
	     "ppd_s": "ppd",
	     "status_s": "status",
         "location": "location"}
FIELD_ARRAYS=["saon_t", "paon_t", "street_t", "locality_t", "town_t", "district_t", "county_t"]

def resolve_zookeeper_string():
    zk_host = os.environ.get("ZK_HOST", "zookeeper")
    zk_port = os.environ.get("ZK_PORT", "2181")
    zk_chroot = os.environ.get("ZK_CHROOT", "/solr")

    if "," in zk_host:
        return ",".join(["%s:%s" % (ip, zk_port) for ip in zk_host.split(",")]) + zk_chroot
    try:
        dummy, dummy, addresses = socket.gethostbyname_ex(zk_host)
    except:
        addresses = []
    if len(addresses)<2:
        return "%s:%s%s" % (zk_host, zk_port, zk_chroot)
    else:
        addresses = ["%s:%s" % (ip, zk_port) for ip in addresses]
        return ",".join(addresses) + zk_chroot

@app.before_first_request
def before_first_request():
  zk = resolve_zookeeper_string()
  app.solr = pysolr.SolrCloud(pysolr.ZooKeeper(zk), "houseprices")

@app.route("/")
def root():
  return send_from_directory("app", "index.html")

@app.route("/js/<name>")
def static_js(name):
  return send_from_directory("app/js", name)

@app.route("/css/<name>")
def static_css(name):
  return send_from_directory("app/css", name)

@app.route("/lib/<path:name>")
def static_lib(name):
  return send_from_directory("app/lib", name)

@app.route("/partials/<path:name>")
def static_partials(name):
  return send_from_directory("app/partials", name)

def convert_sale_format(sale):
  fields = {}
  for name, value in sale.items():
    field_name = FIELD_NAMES.get(name, None)
    if not field_name:
      print "Skipping %s" % name
    elif field_name == "postcode":
      fields[field_name] = value.replace("_", " ")
    elif name == "location":
      fields[field_name] = value[0]
      lat, lon = value[0].split(",")
      fields["lat"]=float(lat)
      fields["lon"]=float(lon)
    elif name in FIELD_ARRAYS:
      if len(value)==0:
        fields[field_name] = ""
      else:
        fields[field_name] = value[0]
    else:
      fields[field_name] = value
  return fields

@app.route("/api/sales")
def houseprice_search():
  postcode = request.args.get("postcode")
  if postcode:
    postcode = postcode.replace(" ", "_")
  date_start = request.args.get("date_start")
  date_end = request.args.get("date_end")
  southwest = request.args.get("southwest", "")
  northeast = request.args.get("northeast", "")
  rows = int(request.args.get("rows", "10"))
  query_parts = []
  if postcode:
    query_parts.append("postcode_s:%s*" % postcode)
  if date_start and date_end:
    query_parts.append("transaction_date_dt:[%s TO %s]" % (date_start, date_end))
  elif date_start:
    query_parts.append("transaction_date_dt:[%s TO *]" % (date_start))
  elif date_end:
    query_parts.append("transaction_date_dt:[* TO %s]" % (date_end))

  if len(query_parts)==0:
    query = "*:*"
  else:
    query = " AND ".join(query_parts)

  params = {"rows": rows,
            "sort": "postcode_s asc"}
  results = app.solr.search(query, **params)
  sales = [convert_sale_format(sale) for sale in results.docs]

  resp = {"hits": results.hits, "sales": sales}
  return jsonify(resp)

def run():
  app.run("0.0.0.0", 8080, debug=True)

