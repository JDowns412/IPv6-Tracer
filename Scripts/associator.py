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
import os, json, pprint, requests, re, urllib.request, argparse
from bs4 import BeautifulSoup

def reader(length, experiment):
    with open("../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        goalLength = length
        file = "top%sEven" % str(goalLength)
        location = "../Data/" + file + ".json"
        data = {}

        # read in and organize the list of sites we want to experiment on
        with open(location, "r") as f:
            data = json.load(f)
        sites = data["sites"]
        
        print("\n______________________associator.py______________________\n")
        print("read in %d sites from %s" %(len(sites), location))
        log.write("\n______________________associator.py______________________\n")
        log.write("read in %d sites from %s" %(len(sites), location))
        return(sites)


# due to the volatile nature of website content, this should be run
# every time we wan to run an experiment
def obj_associator(sites, experiment):
    with open("../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        data = {"exceptions" : {}, "zeros" : [], "valid": {}, "progress" : ["A"]}

        for dom in range(len(sites)):

            # added this line because the script was hanging on these sites
            if (sites[dom] != "jabong.com" and sites[dom] != "bestbuy.com"):
                try:
                    # print (dom)
                    # response = requests.get()
                    domain = "http://www." + sites[dom]
                    print("\nGetting %d/%d: %s" % (dom+1, len(sites), domain))
                    log.write("\nGetting %d/%d: %s" % (dom+1, len(sites), domain))

                    req = urllib.request.Request(domain, headers={'User-Agent': 'Mozilla/5.0'})

                    html_page = urllib.request.urlopen(req)
                    soup = BeautifulSoup(html_page, "lxml")

                    # pprint.pprint(soup.prettify())

                    objects = []

                    # iterate through all the types of website objects that 
                    # we're willing to use for our future requests

                    types = ["ico", "jpg", "jpeg", "png", "gif", "avi", "doc", "mp4", "mp3", "mpg", "mpeg", "txt", "wav", "pdf", "tiff", "mov"]
                    tags = ["img", "meta", "link"]
                    for tag in tags:
                        for obj in soup.findAll(tag):
                            # print("FOUND")
                            if (tag == "img"):
                                o = obj.get('src')
                                if (o is not None and (o[-3:] in types or o[-4:] in types)):
                                    # TODO: check if there is a domain name at the start of the link 
                                    objects.append(o)
                            elif (tag == "meta"):
                                o = obj.get('content')
                                if (o is not None and (o[-3:] in types or o[-4:] in types)):
                                    # TODO: check if there is a domain name at the start of the link 
                                    objects.append(o)
                            elif (tag == "link"):
                                o = obj.get('href')
                                if (o is not None and (o[-3:] in types or o[-4:] in types)):
                                    # TODO: check if there is a domain name at the start of the link 
                                    objects.append(o)
                            # print(o[-3:])

                    if (len(objects) == 0):
                        print("Couldn't find any objects for ", domain)
                        log.write("Couldn't find any objects for ", domain)
                        data["zeros"].append(sites[dom])
                    else:
                        print("Found %d objects for %s" % (len(objects), domain))
                        log.write("Found %d objects for %s" % (len(objects), domain))
                        data["valid"][sites[dom]] = {"objects" : objects}

                except Exception as exception:
                    name = repr(exception).split('(')[0]
                    print("%s exception encountered while requesting %s" % (name, domain))
                    log.write("%s exception encountered while requesting %s" % (name, domain))
                    data["exceptions"][sites[dom]] = name


        # with open("temp.txt", "wb") as w:
        #     w.write(soup.prettify().encode('utf8'))
        return (data)


def dumper(data, goalLength, experiment):
    with open("../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        fileName = ("results")
        os.chdir('../Results/Associated')

        for elem in data["progress"]:
            fileName += "_" + elem
        fileName += "[" + str(goalLength) + "]"

        # if we're actually setting the experiment number, probably through runner.py
        if (experiment != -1):
            fileName += str(experiment)

        fileName += ".json"

        print("\ndumping results to ../Results/Associated/", fileName)
        log.write("\ndumping results to ../Results/Associated/", fileName)

        with open(fileName, 'w') as fp:
            json.dump(data, fp, indent=4)


def run():
    goalLength = 100
    experiment = -1
    parser = argparse.ArgumentParser()
    parser.add_argument(action="store", dest="goalLength", nargs="?")
    parser.add_argument(action="store", dest="experiment", nargs="?")
    args = parser.parse_args()

    # apply the inputted arguments
    if (args.goalLength):
        goalLength = args.goalLength
    if (args.experiment):
        experiment = args.experiment

    # read in the list of hostnames we want to analyze
    sites = reader(goalLength, experiment)

    # go to each of the hostnames and find an object that we can use 
    # for collecting results on
    data = obj_associator(sites, experiment)

    # dump our results out to a JSON to be analyzed later
    dumper(data, goalLength, experiment)



if __name__ == "__main__":
    run()