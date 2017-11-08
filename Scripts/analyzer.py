import os, json, pprint, subprocess, time, socket, re, argparse

def reader(length, experiment):

    goalLength = length
    os.chdir('../Results/Cleaned')
    file = "results_A_C[%s]%s.json" % (str(length), str(experiment))
    location = "../Results/Cleaned"
    data = {}

    # read in and organize the list of sites we want to experiment on
    with open(file, "r") as f:
        data = json.load(f)
    
    print("\n______________________analyzer.py______________________\n")
    print("read in  data dictionary from ", location+file)
    return(data)


def dns_looker(inData):

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

    data["progress"].append("D")

    return (data)


def get(domain, data, version):
# initialize the proper socket version based off of the passed in version
    if (version == 4):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # start the socket connection
        sock.connect((domain, 80))
    else:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        # start the socket connection
        # print(data["valid"][domain]["best6"])
        sock.connect((data["valid"][domain]["best6"], 80))
    
    # construct the message we'll be sending
    message =  'GET ' + data["valid"][domain]["preferred"] + ' HTTP/1.1\r\n'
    message += 'Host: ' + domain + '\r\n'
    message += 'Connection: keep-alive\r\n'
    message += 'User-Agent: Mozilla/5.0\r\n'
    #this double CR-LF is the standard HTTP way of indicating the end of any HTTP header fields
    message += '\r\n'
    
    #record the time the request takes
    start = time.time()
    sock.send(message.encode('utf-8'))
    # receive the response and parse it into it's different header fields
    response = sock.recv(1024)
    # record the time it takes for the object to be fetched (in seconds)
    timer = time.time() - start

    # close the socket once we're done with it
    sock.close()

    return (timer, len(response))


def calibrate6(data, domain):

    # pprint.pprint(data["valid"][domain])

    print("\nRunning IPv6 calibration on ", domain)
    out = ""
    best = 999999999
    for six in data["valid"][domain]["sixes"]:
        # print(six)
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        
        # start the socket connection
        sock.connect((six, 80))

        # construct the message we'll be sending
        message =  'GET ' + data["valid"][domain]["preferred"] + ' HTTP/1.1\r\n'
        message += 'Host: ' + domain + '\r\n'
        message += 'Connection: keep-alive\r\n'
        message += 'User-Agent: Mozilla/5.0\r\n'
        #this double CR-LF is the standard HTTP way of indicating the end of any HTTP header fields
        message += '\r\n'
        
        #record the time the request takes
        start = time.time()
        sock.send(message.encode('utf-8'))
        # receive the response and parse it into it's different header fields
        response = sock.recv(1024)
        # record the time it takes for the object to be fetched (in seconds)
        timer = time.time() - start

        if (timer < best):
            best = timer
            out = six

        sock.close()

    return out


def trace(inData, iterations):
    data = inData

    # do traces for every domain
    count = 0
    for domain, val in data["valid"].items():
        count += 1
        try:
            data["valid"][domain]["results"] = {4 : []}
            # run connections for each IPv4
            print("Tracing %d/%d %s with IPv4" % (count, len(data["valid"]), domain))
            for itr in range(iterations):
                data["valid"][domain]["results"][4].append(get(domain, data, 4))
            
            # run connections for IPv6 (if the domain has it)
            if (data["valid"][domain]["6Support"]):
                data["valid"][domain]["results"][6] = []
                print("Tracing %s with IPv6" % (domain))

                # we need to calibrate the IPv6 first (this is automatic with IPv4, 
                # but not 6 since python's socket module was throwing errors at me)
                data["valid"][domain]["best6"] = calibrate6(data, domain)
                for itr in range(iterations):
                    data["valid"][domain]["results"][6].append(get(domain, data, 6))
            else:
                print("%s does not support IPv6." % domain)

        except Exception as exception:
            name = repr(exception).split('(')[0]
            if (name == "OSError"):
                print ("Having IPv6 connectivity issues with %s. Check your network connection" % domain)
            else:
                print("%s exception encountered while tracing %s" % (name, domain))
                data["exceptions"][domain] = "TRACE... " + name

    # mark the data as "T" for "Traced/Timed"
    data["progress"].append("T")
    return (data)


def dumper(data, goalLength, experiment):

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
    data = dns_looker(data)


    iterations = 10
    # compare access speeds for the different sites
    data = trace(data, iterations)

    # dump our results out to a JSON to be analyzed later
    dumper(data, goalLength, experiment)



if __name__ == "__main__":
    run()    
