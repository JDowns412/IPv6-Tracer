import os, json, pprint, subprocess, time, socket, re, argparse

def reader(length, experiment):
    with open("../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        goalLength = length
        os.chdir('../Results/Cleaned')
        file = "results_A_C[%s]%s.json" % (str(length), str(experiment))
        location = "../Results/Cleaned"
        data = {}

        # read in and organize the list of sites we want to experiment on
        with open(file, "r") as f:
            data = json.load(f)
        
        print("\n______________________analyzer.py______________________\n")
        log.write("\n______________________analyzer.py______________________\n")
        print("read in  data dictionary from ", location+file)
        log.write("read in  data dictionary from %s" % str(location+file))
        return(data)


def dns_looker(inData, experiment):
    with open("../../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        data = inData
        count = 0

        # iterate through every domain in data["valid"], 
        # since those are the only applicable domains to this experiment
        for domain, val in data["valid"].items():
            # run the IPv6 DNS lookup on the domain
            proc = subprocess.Popen(["nslookup", "-q=aaaa", domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
            # parse the response
            res = str(proc.communicate())
            
            # store whether or not the website supports IPv6 or not
            data["valid"][domain]["6Support"] = ("***" not in res)

            # keep count of how many sites don;t support IPv6
            if ("***" in res):
                count += 1
            else:
                # find all the IPv6 addresses for this domain, to be used later
                temp = re.findall(r' [a-z0-9]*[:[a-z0-9]*]*\\', res)[0:-1]
                sixes = []
                for six in temp:
                    sixes.append(six[1:-2])

                data["valid"][domain]["sixes"] = sixes


        print("\n%d/%d sites don't support IPv6\n" % (count, len(data["valid"])))
        log.write("\n%d/%d sites don't support IPv6\n" % (count, len(data["valid"])))

        data["progress"].append("D")

        return (data)


def get(domain, data, version, experiment):
    with open("../../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        # initialize the proper socket version based off of the passed in version
        if (version == 4):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # start the socket connection
            sock.connect((domain, 80))
        else:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            # start the socket connection
            # print(data["valid"][domain]["best6"])
            # sock.connect((data["valid"][domain]["best6"], 80, 0, 0))
            addrs = socket.getaddrinfo(domain, 80, socket.AF_INET6, 0, socket.SOL_TCP)
            # print(addrs)
            sockaddr = addrs[0][-1]
            # print(sockaddr)
            sock.connect(sockaddr)

        # set a timeout
        sock.settimeout(10)

        # construct the message we'll be sending
        message =  'GET ' + data["valid"][domain]["preferred"] + ' HTTP/1.1\r\n'
        message += 'Host: ' + domain + '\r\n'
        message += 'Connection: keep-alive\r\n'
        message += 'User-Agent: Mozilla/5.0\r\n'
        #this double CR-LF is the standard HTTP way of indicating the end of any HTTP header fields
        message += '\r\n'

        # make sure that we are out of TCP slow start
        cold = True
        # threshold is the percentage of difference that we want our response times to be within
        threshold = .25
        warmUp = 100
        fiveInRow = False
        lastFive = []
        times = []
        count = 0
        while(cold):
            if (count > 500):
                # only way to stop an infinite loop... 500 requests is probably out of slow start
                cold = False
                print("\tHad to hard-code a break out of slow start")
                log.write("\tHad to hard-code a break out of slow start")

            if (count % 100 == 0):
                # print("Leaving slow-start...", end='')
                log.write("\tLeaving slow-start...")
            # receive the object
            sock.send(message.encode('utf-8'))
            #record the time the request takes
            start = time.time()
            # receive the response and parse it into it's different header fields
            response = sock.recv(65535)
            # record the time it takes for the object to be fetched (in seconds)
            timer = time.time() - start
            times.append(timer)
            count += 1

            # if we've requested at least the 100 times as a blind warm up
            # start checking for ideal (non-slow start) conditions after 100 times
            if (count >= warmUp):
                # if the last 5 objects were within the specified threshold of difference
                # keep track of only the last 5 requests
                if(len(lastFive) >= 5):
                    lastFive.pop(0)

                # find the time difference in the second to last and last request
                diff = times[-2] - times[-1]

                low = min(times[-2], times[-1])
                high = max(times[-2], times[-1])

                # (numbers within threshold of each other, latest request was longer then the previous one)
                # we are looking for a longer request to help us know that we are 
                # not still improving our time like slow start does
                lastFive.append(((low+low*threshold > high-high*threshold), (diff < 0)))

                # if we're at a point where we can decide that we are out of slow start
                if(len(lastFive) == 5):
                    thresh = 0
                    slower = 0

                    for elem in lastFive:
                        if (elem[0]):
                            thresh += 1
                        if (elem[1]):
                            slower += 1

                    # if the majority of requests are positive indications, we're out of cold start
                    if (thresh >= 3 and slower >= 2):
                        cold = False
                        print("\t...done leaving slow start")
                        log.write("\t...done leaving slow start")

        # run this for 10 iterations for average speeds
        iterations = 10

        out = []
        for i in range(iterations):
            sock.send(message.encode('utf-8'))
            #record the time the request takes
            start = time.time()
            # receive the response and parse it into it's different header fields
            response = sock.recv(65535)
            # record the time it takes for the object to be fetched (in seconds)
            timer = time.time() - start

            out.append((timer, len(response)))

        # close the socket once we're done with it
        sock.close()

        return out


# def calibrate6(data, domain):

#     # pprint.pprint(data["valid"][domain])

#     print("\nRunning IPv6 calibration on ", domain)
#     out = ""
#     best = 999999999
#     for six in data["valid"][domain]["sixes"]:
#         # print(six)
#         sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        
#         # start the socket connection
#         # sock.connect((six, 80, 0, 0))
#         addrs = socket.getaddrinfo(six, 80, socket.AF_INET6, 0, socket.SOL_TCP)
#         # print(addrs)
#         sockaddr = addrs[0][-1]
#         # print(sockaddr)
#         sock.connect(sockaddr)

#         # construct the message we'll be sending
#         message =  'GET ' + data["valid"][domain]["preferred"] + ' HTTP/1.1\r\n'
#         message += 'Host: ' + domain + '\r\n'
#         message += 'Connection: keep-alive\r\n'
#         message += 'User-Agent: Mozilla/5.0\r\n'
#         #this double CR-LF is the standard HTTP way of indicating the end of any HTTP header fields
#         message += '\r\n'
        
#         #record the time the request takes
#         start = time.time()
#         sock.send(message.encode('utf-8'))
#         # receive the response and parse it into it's different header fields
#         response = sock.recv(1024)
#         # record the time it takes for the object to be fetched (in seconds)
#         timer = time.time() - start

#         if (timer < best):
#             best = timer
#             out = six

#         sock.close()

#     return out


def trace(inData, iterations, experiment):
    with open("../../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        data = inData

        # do traces for every domain
        count = 0
        for domain, val in data["valid"].items():
            if "preferred" in data["valid"][domain]:
                count += 1
                # if(1 == 1):
                try:
                    data["valid"][domain]["results"] = {4 : []}
                    # run connections for each IPv4
                    print("Tracing %d/%d %s with IPv4" % (count, len(data["valid"]), domain))
                    log.write("Tracing %d/%d %s with IPv4" % (count, len(data["valid"]), domain))
                    results = get(domain, data, 4, experiment)
                    for result in results:
                        data["valid"][domain]["results"][4].append(result)
                    
                    # run connections for IPv6 (if the domain has it)
                    if (data["valid"][domain]["6Support"]):
                        data["valid"][domain]["results"][6] = []
                        print("Tracing %s with IPv6" % (domain), end='')
                        log.write("Tracing %s with IPv6" % (domain))

                        # we need to calibrate the IPv6 first (this is automatic with IPv4, 
                        # but not 6 since python's socket module was throwing errors at me)
                        # data["valid"][domain]["best6"] = calibrate6(data, domain)
                        results = get(domain, data, 6, experiment)
                        for result in results:
                            data["valid"][domain]["results"][6].append(result)

                        # collect some basic trace route data on the sites that support both v4 and v6
                        # IPv4 trace
                        print("...IPv4 trace route...", end='')
                        log.write("Performing IPv4 trace route")

                        proc = subprocess.Popen(["tracert", "-4", domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
                        res = str(proc.communicate())
                        data["valid"][domain]["4trace"] = {"raw" : res, "hops" : 0}
                        # count the number of hops in the trace route
                        for line in res.split("\\r\\n"): 
                            data["valid"][domain]["4trace"]["hops"] += int("timed out" not in line)

                        print("IPv6 trace route.")
                        log.write("Performing IPv6 trace route")

                        # IPv6 trace
                        proc = subprocess.Popen(["tracert", "-6", domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
                        res = str(proc.communicate())
                        data["valid"][domain]["6trace"] = {"raw" : res, "hops" : 0}
                        # count the number of hops in the trace route
                        for line in res.split("\\r\\n"): 
                            data["valid"][domain]["6trace"]["hops"] += int("timed out" not in line)

                    else:
                        print("%s does not support IPv6." % domain)
                        log.write("%s does not support IPv6." % domain)

                except Exception as exception:
                    name = repr(exception).split('(')[0]
                    if (name == "OSError"):
                        print ("Having IPv6 connectivity issues with %s. Check your network connection" % domain)
                        log.write ("Having IPv6 connectivity issues with %s. Check your network connection" % domain)
                    else:
                        print("%s exception encountered while tracing %s" % (name, domain))
                        log.write("%s exception encountered while tracing %s" % (name, domain))
                        data["exceptions"][domain] = "TRACE... " + name

        # mark the data as "T" for "Traced/Timed"
        data["progress"].append("T")
        return (data)


def dumper(data, goalLength, experiment):
    with open("../../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        fileName = ("results")
        os.chdir('../Analyzed')

        for elem in data["progress"]:
            fileName += "_" + elem
        fileName += "[" + str(goalLength) + "]"

        # if we're actually setting the experiment number, probably through runner.py
        if (experiment != -1):
            fileName += str(experiment)

        fileName += ".json"

        print("\ndumping results to ../Results/Analyzed", fileName)
        log.write("\ndumping results to ../Results/Analyzed%s" % fileName)

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

    # read in the the data we got from associator.py
    data = reader(goalLength, experiment)

    # go to each of the hostnames and find an object that we can use 
    # for collecting results on
    data = dns_looker(data, experiment)


    iterations = 1
    # compare access speeds for the different sites
    data = trace(data, iterations, experiment)

    # dump our results out to a JSON to be analyzed later
    dumper(data, goalLength, experiment)



if __name__ == "__main__":
    run()    
