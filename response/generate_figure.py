#!/usr/bin/python
#encoding:utf-8

import matplotlib
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger('django')

def generate_days_trend_curve(image_file, x_range, y_array):
    fig = plt.figure(figsize=(3,1.75))
    fig.suptitle('Active level in 9 days', fontsize=8)
    plt.xlabel('date', fontsize=3)
    plt.ylabel('seconds', fontsize=3)
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
#    x_array = np.linspace(-3,3,10)
#    y = np.sin(x)
    x_array = np.linspace(1,x_range,x_range)
#    logger.info(str(x_array))
    plt.plot(x_array, y_array, '--*r')    
    fig.savefig(image_file)

def generate_cur_cpu_bar(image_file, x_list, y_list):
    fig = plt.figure(figsize=(3,1.75))
    fig.suptitle('Current CPU utiization of instances', fontsize=8)
    num_vm = len(y_list)
    logger.info(num_vm)
    bar_left_list = []
    bar_bottom = [0] * num_vm
    bar_width = [0.6] * num_vm

    max_y_list = max(y_list)
    if max_y_list >= 1:
        max_val = max(y_list) + 0.1
        plt.ylim(0, max_val)
    else:
	if (max_y_list<1) and (max_y_list>=0.1):
	    plt.ylim(0, 1)
	else:
	    if (max_y_list<0.1) and (max_y_list>=0.01):
                plt.ylim(0, 0.1)
    	    else:
		plt.ylim(0, 0.01)

    plt.xlim(0, num_vm + 1)

    for i in range(num_vm):
        bar_left_list.append(i + 1)

    plt.xticks(bar_left_list, x_list)

    ax = fig.add_subplot(111)
    logger.info(str(bar_left_list) + str(y_list) + str(bar_width) + str(bar_bottom))
    rects = ax.bar(bar_left_list, y_list, bar_width, bar_bottom,
                   color='#ffff00',
                   edgecolor='#000000',
                   linewidth=1,
                   #xerr=4,
                   #yerr=1,
                   #ecolor='#999999',
                   #capsize=10,
                   #align='center',
                   #orientation='horizontal',
                  )

    plt.savefig(image_file)   


