#!/usr/bin/env python
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
import logging

logger = logging.getLogger('django')

def get_counter_val(es, server_id, counter_name, start_time, end_time):
    logger.info(str(es))
    result = es.search(index="_all", body = make_query(start_time, end_time, server_id, counter_name))
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
	logger.info("no result return")
        return 0

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

