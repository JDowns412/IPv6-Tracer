# This script is going to take in the JSON that's 
# output from analyzer.py, and output graphs of statistics from 
# the conclusions that analyzer.py found in the 'Figures' directory

import json
import numpy as np
import matplotlib.pyplot as plt


def jgraph(data):
	valids = data.get("valid")
	ipv4_results = []
	ipv6_results = []
	for k,v in valids.items():
		results = v["results"]
		#print(results)
		if len(results["4"])>1:
			res = []
			for x,y in results["4"]:
				res.append(x)
			ipv4_results.append(numpy.mean(res))
		if "6" in results.keys() and len(results["6"])>1:
			res = []
			for x,y in results["6"]:
				res.append(x)
			ipv6_results.append(numpy.mean(res))
	print(len(ipv4_results))
	bins = numpy.linspace(0,.1)
	plt.hist(ipv4_results, bins, alpha=0.5, label='IPv4')
	plt.hist(ipv6_results, bins, alpha=0.5, label='IPv6')
	# plt.xticks(numpy.arange(min(ipv4_results), max(ipv4_results)+1, .01))
	plt.legend(loc='upper right')
	plt.show()

def tgraph(data):
	# csv_results: domain, ipv4 mean time, ipv6 mean time
	csv_results = []
	for domain in data["valid"]:
		if "results" in data["valid"][domain]:
			results = data["valid"][domain]["results"]
			if "4" in results and results["4"] and "6" in results and results["6"]:
				ipv4_means = np.mean(results["4"], axis=0)
				ipv4_time = ipv4_means[0]
				ipv4_size = ipv4_means[1]
				ipv4 = (ipv4_size / ipv4_time) / 1024.0 # kb/s
				ipv6_means = np.mean(results["6"], axis=0)
				ipv6_time = ipv6_means[0]
				ipv6_size = ipv6_means[1]
				ipv6 = (ipv6_size / ipv6_time) / 1024.0 # kb/s
				csv_results.append([domain, ipv4, ipv6])
	csv_results.sort(key=lambda x: x[2])
	with open("comparison.csv", 'w') as f:
		for row in csv_results:
			f.write(','.join([str(r) for r in row]))
			f.write('\n')

def tstats(data):
	ipv6 = 0
	total = 0
	for domain in data["valid"]:
		total += 1
		if "6Support" in data["valid"][domain] and data["valid"][domain]["6Support"]:
			ipv6 += 1
	print("{} / {} = {}".format(ipv6, total, ipv6 / total))

if __name__ == '__main__':
	with open('../Results/Analyzed/results_A_C_D_T[500]16.json') as data_file:
		data = json.load(data_file)
		# jgraph(data)
		# tgraph(data)
		tstats(data)