'''
Overall functionality goal: 
-Take in a list of addresses, output a JSON that contains stats 
    collected on each hostname concerning IPv4/IPv6 support.

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
    -Create a list called records that will keep track of whatever things 
     were done to the data.
        -Add an ‘A’ to mark the data as “associated with an object”
    -Return (data, records)

dns_looker(data, records)
    -For each hostname in the data dictionary, run AAA DNS lookups and add an entry 
     for every hostname on whether or not it has an IPv6 address associated with it
    -Use either a DNS library or the requests module to run DNS lookups and parse 
     the results to determine if an AAA address is present for each site
    -Set the “ipv6” boolean for each site in the dictionary
    -Add a ‘D’ to mark the data as “having an IPv6 address or not in DNS”
    -Return (data, records)

tracer(data, records)
    -Run IPv4/6 traces on the websites and time them 
        -Request the objects associated by obj_associator in both IPv4/6, using either 
         some requests library, or manually request it on the command line
        -Incorporate some sort of timer, start it right before the request, and end 
         it right after the request. Add the timings to the data dictionary
    -Add a ‘T’ to mark the data as “traced for IPv4/6”
    -Return (data, records)

dumper(data, records)
    -Generate a filename for the outputted JSON based off of the records list
    -Dump the json into the data directory
'''