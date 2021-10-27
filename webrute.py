
import threading
import queue 
import urllib
import urllib.parse
import urllib.error
import urllib.request
import sys 
import getopt
import usage 



threads = 5
target_url = "http://testaspnet.vulnweb.com" 
worldlist = "/tmp/wordlist.txt" 
resume_from_here = None   #we will use this to resume our brute forcing if connection is interrupted or target goes down
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"

#read from command line
try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "ht:u:w:r:a:",
        ["help","threads","url","wordlist","resume","useragent"]
    )
except getopt.GetoptError as err :
    print(str(err))
    usage.helper()
    sys.exit(0)

for o,a in opts:
    if o in ("-h","--help"):
        usage.helper()
        sys.exit(0)
    elif o in ("-t","--threads"):
        threads = a
    elif o in ("-u","--url"):
        target_url = a
    elif o in ("-w","--wordlist"):
        wordlist = a
    elif o in ("-r","--resume"):
        resume_from_here = a 
    elif o in ("-a","--useragent"):
        user_agent = a
    else :
        assert False , "Unhandled Option"


def initialize_wordlist(wordlist):

    #we read the wordlist
    fd = open(wordlist,"r")
    wl_words = fd.readlines()
    fd.close()

    run = False  # we use this boolean to resume brute forcing from another point of the wordlist
    q_words = queue.Queue()

    for wd in wl_words :

        wd = wd.rstrip() #we remove space at the end of each string in the wordlist

        if resume_from_here is not None :  

            if run :
                q_words.put(wd)
            else:
                if wd == resume_from_here : #we read the wordlist until we meeting the word we have passed to the script
                    run = True
                    print ("Start reading wordlist from ' %s '" % resume_from_here)

        else :
            q_words.put(wd)
    
    return q_words

def bruter(queue_words, extensions=None):
    while not queue_words.empty():
        attempt = queue_words.get()
        attempt_list = []

        #we control if the file has an ext
        # if not , it's a directory path
        
        if "." not in attempt :
            attempt_list.append("%s/" % attempt)
        else :
            attempt_list.append("%s"  % attempt)
        
        
        #if we want do extensions brute forcing

        if extensions :
            for ext in extensions :
                attempt_list.append(
                    "%s%s" % (attempt,ext))
        
        #we iterate on our attempts list
        for brute in attempt_list :

            url = "%s/%s" %(target_url,urllib.parse.quote(brute)) #url parsing

            try :
                headers = {}
                headers["User-Agent"] = user_agent
                req = urllib.request.Request(url,headers=headers) 

                response = urllib.request.urlopen(req)

                if len(response.read()) :
                    print ("%s => %d status code" %(url,response.code))
                
            except urllib.error.HTTPError as e :

                if hasattr(e,'code') and e.code != 404 : #we 
                    print ("[!!!] PARTICULAR RESPONSE : %s => %d status code " %(url,e.code))

                pass
            

queue_words = initialize_wordlist(worldlist)
extensions = [".php",".bak",".orig",".inc"]

for i in range(threads) :
    t = threading.Thread(target=bruter,args=(queue_words,extensions,))
    t.start()

