import subprocess, json, os, argparse

def reader():

    file = "tracker.json"
    location = "../Results/" + file
    data = {}

    # read in and organize the list of sites we want to experiment on
    with open(location, "r") as f:
        data = json.load(f)
    
    print("Running experiment #%s" % str(data["count"]+1))
    return(data)



def dumper(data):

    fileName = ("tracker.json")
    os.chdir('../Results')

    print("\nTracker JSON has been updated. Terminating...")

    with open(fileName, 'w') as fp:
        json.dump(data, fp, indent=4)



def run():
    goalLength = 100
    parser = argparse.ArgumentParser()
    parser.add_argument(action="store", dest="goalLength", nargs="?")
    args = parser.parse_args()

    # apply the inputted arguments
    if (args.goalLength):
        goalLength = args.goalLength

    print("HEHEHEE", goalLength)

    tracker = reader()

    # call the associator script
    subprocess.call(["python3", "associator.py", str(goalLength), str(tracker["count"])])

    os.chdir('../Scripts')

    # call the cleaner script
    subprocess.call(["python3", "cleaner.py", str(goalLength), str(tracker["count"])])

    os.chdir('../Scripts')

    # call the analysis script
    subprocess.call(["python3", "analyzer.py", str(goalLength), str(tracker["count"])])

    os.chdir('../Scripts')

    # increment the experiment number to signify another successful experiment 
    # (we can't get to this point if we hung on some weird error and never 
    # terminated the experiment)
    tracker["count"] += 1
    dumper(tracker)

    # shutdown windows (Used to test models overnight)
    # subprocess.call(["shutdown", "/s"])

if __name__ == "__main__":
    run()