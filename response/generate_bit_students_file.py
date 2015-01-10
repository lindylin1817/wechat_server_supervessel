#!/usr/bin/python
#encoding:utf-8

from pyExcelerator import *
from models import Users, virtualmachines
from mongoengine import Q
import logging

master_name = "master_node"
slave_prefix = "slave_node_"
num_slave = 3

logger = logging.getLogger('django')

def gen_students_xls(students_file_xls):

    w = Workbook()
    ws_cpu = w.add_sheet(u"CPU activity")
    ws_network = w.add_sheet(u"Network activity")
    
    font0 = Font()
    font0.name = 'Times New Roman'
    font0.struck_out = False
    font0.bold = True

    style0 = XFStyle()
    style0.font = font0
    style1 = XFStyle()
    style1.num_format_str = "0"

    ####################### To prepare header ##########
    ws_cpu.write(1, 1, u"This is the average CPU utilization (%) for each instance in the past 24 hours", style0)
    ws_network.write(1, 1, u"This is the total bytes of data over network (in K) in the past 24 hours.", style0)
    ws_cpu.write(3, 2, u"master_node", style0)
    ws_network.write(3, 2, u"master_node", style0)

    for i in range(num_slave):
	slave_name = slave_prefix + str(i+1)
	ws_cpu.write(3, 2 + i + 1, slave_name, style0)
	ws_network.write(3, 2 + i + 1, slave_name, style0)

    ############### To prepare real data ##################
    logger.info("To prepare real data for xls file")

    masters = virtualmachines.objects(vm_name=master_name)
    index_master = 0

    for master_node in masters:
#	logger.info(str(index_master))

	the_user = master_node['supervessel_account']
	if (the_user!="admin") and (the_user.find('ibm.com')<0):
  	    raw_index = 4 + index_master
	    ws_cpu.write(raw_index, 1, the_user, style0)
            ws_network.write(raw_index, 1, the_user, style0)
	    val_cpu = int(master_node.cpu_usage_list[-1]/24.0/3600.0*100)
	    val_network = master_node.network_usage_list[-1]
            ws_cpu.write(raw_index, 2, val_cpu, style1)
	    ws_network.write(raw_index, 2, val_network, style1)

	    for i in range(num_slave):

	        slave_name = slave_prefix + str(i+1)
	        the_slave = virtualmachines.objects(Q(vm_name=slave_name) & Q(supervessel_account=master_node['supervessel_account'])).first()
                val_cpu = int(the_slave.cpu_usage_list[-1]/24.0/3600.0*100)
	        val_network = the_slave.network_usage_list[-1]
	        ws_cpu.write(4 + index_master, 2 + i + 1, val_cpu, style1)
	        ws_network.write(4 + index_master, 2 + i + 1, val_network, style1)
	    index_master = index_master + 1

    w.save(students_file_xls)
