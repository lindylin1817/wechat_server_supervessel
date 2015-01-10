#!/usr/bin/python
#encoding:utf-8

#from elasticsearch_query import get_counter_val
from models import virtualmachines
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection
from time import time as timest
import json

logger = logging.getLogger('django')

def get_cur_cpu_usage(supervessel_account):

    vm_list = virtualmachines.objects(
                        supervessel_account = supervessel_account)

    result={'name_list':[],'cpu_usage_list':[]}

    if not vm_list:
        return False
    else:
        try:
            es = Elasticsearch([dict(host = "crl.ptopenlab.com", 
			port = 8800, http_auth = ("admin", "p0weradm1n"), 
			use_ssl=True, url_prefix = "elasticsearch")], 
			connection_class = RequestsHttpConnection)
        except:
            logger.info("Cannot connect to remote elastic search server")
            return False
	else:
	    logger.info("Connected to search server")

	now = timest() * 1000        
        start_time = (timest() - 60 * 60) * 1000
	end_time = now
#        logger.info(str(start_time))
#	logger.info(str(end_time))
	name_list = []
	cpu_usage_list = []
	for vm in vm_list:
	    cpu_usage_list.append(float(get_counter_val(es, vm['vm_id'], "cpu", 
			start_time, end_time)/60.000/60.000))
	    name_list.append(vm['vm_name'])

	result['name_list'].append(name_list)
	result['cpu_usage_list'].append(cpu_usage_list)	    
        return result
    
def make_query(start_time, end_time, resource_id, counter_name) : 
#    now = timest() * 1000

    '''
    return json.dumps(
    {
      "facets": {
        "14": { "date_histogram": { "key_field": "@timestamp", "value_field": "counter_volume", "interval": "1s" },
          "global": True,
          "facet_filter": {
            "fquery": {
              "query": {
                "filtered": {
                  "query": {
                    "query_string": {
                      "query": "(resource_metadata.instance_id:" + resource_id + " OR resource_id:" + resource_id + ") AND (counter_name:" + counter_name + ")"
                    }
                  },
                  "filter": {
                    "bool": {
                      "must": [
                        { "range": { "@timestamp": { "from": start_time, "to": end_time } }
                        }
                      ]
                    }
                  }
                }
              }
            }
          }
        }
      },
      "size": 0
      }
      '''
    return json.dumps(
    {
      "facets": {
        "14": { "date_histogram": { "key_field": "@timestamp", "value_field": "counter_volume", "interval": "1s" },
          "global": True,
          "facet_filter": {
            "fquery": {
              "query": {
                "filtered": {
                  "query": {
                    "query_string": {
                      "query": "(resource_metadata.instance_id:" + resource_id + " OR resource_id:" + resource_id + ") AND (counter_name:" + counter_name + ")"
                    }
                  },
                  "filter": {
                    "bool": {
                      "must": [
                        { "range": { "@timestamp": { "from": start_time, "to": end_time } }
                        }
                      ]
                    }
                  }
                }
              }
            }
          }
        }
      }
      }
    )


def get_counter_val(es, server_id, counter_name, start_time, end_time):
    result = es.search(index="_all", body = make_query(start_time, end_time, server_id, counter_name))
#    logger.info(str(result))
    if len(result["facets"]["14"]["entries"]) > 0 :
        newest = result["facets"]["14"]["entries"][0]["total"]
        oldest = result["facets"]["14"]["entries"][-1]["total"]
        if newest < oldest :
            tmp = oldest
            oldest = newest
            newest = tmp

        val = newest - oldest
#        val = newest
        if counter_name == "cpu" :
            val = val / 1000000000
        if counter_name == "network.outgoing.bytes":
	    val = val / 1024 
	return val
#        keystone = client.Client(token=sys_token, endpoint=sys_endpoint)
#        server_name = server_name_file_obj.readline()
#        user_account = keystone.users.get(user_id)
#        print "User: " + user_account.username + ": " + str(int(val))
#        add_virtualmachine_db(server_id, server_name, user_account.username, val)
    else :
        return 0



