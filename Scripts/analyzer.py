'''
Overall functionality goal: 
-Take in a list of addresses, output a JSON that contains stats 
    collected on each hostname concerning IPv4/IPv6 support.

reader()
    -read in the list of websites from the Data directory
        -(parse through things if necessary)
    -create the Data dictionary and store them in it
    -return(data)

obj_associator(data)
    -For each name in the inputted list run an IPv4 connection to it, and 
     determine an object from the webpage that will be used for 
      benchmarking the speed of the connection
    -Use some sort of requests library to request the page
    -Parse through the page and find some object (a .jpg, .png, .gif etc) 
     to associate with that link. 
        -Output an error if this isn’t possible
    -Then, add the name of this object to the dictionary of the parsed in hostnames.
    -Now, we can refer back to this dictionary and request that object in a 
     later method (the one doing the traceroutes, or other things)
    -Create a list called progress that will keep track of whatever things 
     were done to the data.
        -Add an ‘A’ to mark the data as “associated with an object”
    -Return (data, progress)

dns_looker(data, progress)
    -For each hostname in the data dictionary, run AAAA DNS lookups and add an entry 
     for every hostname on whether or not it has an IPv6 address associated with it
    -Use either a DNS library or the requests module to run DNS lookups and parse 
     the results to determine if an AAAA address is present for each site
    -Set the “ipv6” boolean for each site in the dictionary
    -Add a ‘D’ to mark the data as “having an IPv6 address or not in DNS”
    -Return (data, progress)

tracer(data, progress)
    -Run IPv4/6 traces on the websites and time them 
        -Request the objects associated by obj_associator in both IPv4/6, using either 
         some requests library, or manually request it on the command line
        -Incorporate some sort of timer, start it right before the request, and end 
         it right after the request. Add the timings to the data dictionary
    -Add a ‘T’ to mark the data as “traced for IPv4/6”
    -Return (data, progress)

dumper(data, progress)
    -Generate a filename for the outputted JSON based off of the progress list
    -Dump the json into the Data directory
'''

import os, json

def reader():
    location = "../Data/[fileName]"
    data = {}
    return(data)



def obj_associator(data):
    progress = []
    return (data, progress)



def dns_looker(data, progress):

    return (data, progress)



def tracer(data, progress):

    return (data, progress)



def dumper(data, progress):

    fileName = ("results")
    os.chdir('../Results')

    for elem in progress:
        fileName += "_" + elem
    fileName += ".json"

    with open(fileName, 'w') as fp:
        json.dump(data, fp, indent=4)


def run():
    # read in the list of hostnames we want to analyze
    data = reader()

    # go to each of the hostnames and find an object that we can use 
    # for collecting results on
    data, progress = obj_associator(data)

    # determine if each hostname supports IPv6 or not
    data, progress = dns_looker(data, progress)

    # evaluate access times for IPv4/6 on each host
    data, progress = tracer(data, progress)

    # dump our results out to a JSON to be analyzed later
    dumper(data, progress)



if __name__ == "__main__":
    run()