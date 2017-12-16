import os, json, pprint, subprocess, argparse, pdb

def reader(length, experiment):
    print("EXPERIMENT: ", experiment)
    with open("../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        goalLength = length
        location = "../Results/Analyzed/"
        os.chdir('../Results/Associated')
        file = "results_A[%s]%s.json" % (str(length), str(experiment))
        data = {}

        # read in and organize the list of sites we want to experiment on
        with open(file, "r") as f:
            data = json.load(f)
        
        print("\n______________________cleaner.py______________________\n")
        print("read in  data dictionary from %s" % str(location+"/" +file))
        log.write("\n______________________cleaner.py______________________\n")
        log.write("read in  data dictionary from %s" % str(location+"/" +file))
        return(data)

def clean(inData, experiment):
    # pdb.set_trace()
    with open("../../Logs/Experiment %s.log" % str(experiment), 'a') as log:
        data = inData
        count = 0
        # clean the objects found for every domain
        for domain, val in data["valid"].items():
            # to organize the printing output
            if (count % 100 == 0):
                print()
                log.write("\n")
            data["valid"][domain]["dirty"] = True
            for obj in val["objects"]:
                # best case scenario: we have an object that's in a subdirectory of 
                # the root domain name (and it's not an object with two //'s at the 
                # beginning of it's source url)
                if (obj[0] == "/" and obj[1] != "/"):
                    data["valid"][domain]["preferred"] = obj
                    data["valid"][domain]["dirty"] = False
                    print("1", end='')
                    log.write("1")
                    break
                # second best case scenario, this is likely the same scenario as above, 
                # just missing a / from the parsing process (HTML is sloppy)
                elif (obj[0].isalpha()):
                    data["valid"][domain]["preferred"] = "/"+ obj
                    data["valid"][domain]["dirty"] = False
                    print("2", end='')
                    log.write("2")
                    break
                # third best scenario: just like the first, just with "./ at the beginning"
                if (obj[0] == "." and obj[1] == "/" and obj[2].isalpha()):
                    data["valid"][domain]["preferred"] = obj[1:]
                    data["valid"][domain]["dirty"] = False
                    print("3", end='')
                    log.write("3")
                    break
                # fourth case best scenario: the object is a full URL that contains the domain name, 
                # so it's probably from the domain itself
                elif (domain in obj):
                    data["valid"][domain]["preferred"] = obj
                    data["valid"][domain]["dirty"] = False
                    print("4", end='')
                    log.write("4")
                    break
            count += 1

        # make a second run through to add in the less than preferable choices if 
        # there were no good objects found above. These cases are where there are 
        # url's that start with "//", and usually come from some 
        # CDN associated with the website.
        for domain, val in data["valid"].items():
            # if the object is still dirty
            if (data["valid"][domain]["dirty"]):
                for obj in val["objects"]:
                    if (obj[0:2] == "//" and obj[2].isalpha()):
                        data["valid"][domain]["preferred"] = obj
                        data["valid"][domain]["dirty"] = False
                        print("   5   ", end='')
                        log.write("   5   ")
                        break

        # notify of any remaining dirty domains 
        # (ones that don't have a nice, clean object to request)
        print("\n")
        log.write("\n")
        for domain, val in data["valid"].items():
            if (data["valid"][domain]["dirty"]):
                print("%s is still dirty!!!" % domain)
                log.write("%s is still dirty!!!" % domain)

        # mark this data as "C" for cleaned
        data["progress"].append("C")

        return data

def dumper(data, goalLength, experiment):
    # pdb.set_trace()
    with open("../../Logs/Experiment %s.log" % str(experiment), 'a') as log:

        fileName = ("results")
        os.chdir('../Cleaned')

        for elem in data["progress"]:
            fileName += "_" + elem
        fileName += "[" + str(goalLength) + "]"

        # if we're actually setting the experiment number, probably through runner.py
        if (experiment != -1):
            fileName += str(experiment)

        fileName += ".json"

        print("\ndumping results to ../Results/Cleaned", fileName)
        log.write("\ndumping results to ../Results/Cleaned%s" % fileName)

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

    # find "preferred objects for all of the data"
    data = clean(data, experiment)

    # dump the data out to be processed by analyzer.py
    dumper(data, goalLength, experiment)

    # dump our results out to a JSON to be analyzed later
    # dumper(data)



if __name__ == "__main__":
    run()    