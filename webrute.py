
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
wordlist = "/tmp/wordlist.txt" 
resume_from_here = None   #we will use this to resume our brute forcing if connection is interrupted or target goes down
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
extensions = None # default extensions set
recursive = False
recursive_list = [] # for recursive searching

#read from command line
try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "ht:u:w:r:a:R",
        ["help","threads","url","wordlist","resume","useragent","recursive"]
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
        threads = int(a)
    elif o in ("-u","--url"):
        target_url = a
    elif o in ("-w","--wordlist"):
        wordlist = a
    elif o in ("-r","--resume"):
        resume_from_here = a 
    elif o in ("-a","--useragent"):
        user_agent = a
    elif o in ("-R","--recursive"):
        recursive = True 
    else :
        assert False , "Unhandled Option"

if len(args) :            #new extensions set defined by user
    extensions = args 

def settings() :
    print("")
    print("Webrute will perform directory brute forcing using these settings : ")
    print("")
    print("threads = "+str(threads))
    print("target url = "+target_url)
    print("wordlist path = "+wordlist)
    print("resume = "+str(resume_from_here))
    print("user agent = "+user_agent)
    print("recursive = "+ str(recursive))
    print("extensions = "+ str(extensions))
    print("")

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
                    q_words.put(wd)
                    print ("Start reading wordlist from ' %s ' \n" % resume_from_here)

        else :
            q_words.put(wd)
    
    return q_words

def bruter(queue_words, extensions=None):
    while not queue_words.empty():
        attempt = queue_words.get()
        attempt_list = []

        # we control if the file has an ext. if not , it's a directory path
        
        if "." not in attempt :
            attempt_list.append("%s/" % attempt)
            if extensions :                         #if extensions are been declared, we add them to dir paths
                for ext in extensions :
                    attempt_list.append("%s%s" % (attempt,ext))

        # we add extensions 
        else :                  
            attempt_list.append("%s"  % attempt)
            if extensions :
                for ext in extensions :
                     if ext not in attempt :
                        string_no_ext = ".".join(attempt.split(".")[:-1])
                        attempt_list.append("%s%s" % (string_no_ext,ext))             
        
        
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
                    if (( response.code == 200 ) and recursive ): 
                        #print (f"Added to the recursive list: {url}")
                        if "." not in ( url.split("/")[-1] ) :
                            recursive_list.append( url )
                      
      
            except urllib.error.HTTPError as e :

                if (hasattr(e,'code') and e.code != 404)  : 
                    print ("COULD BE INTERESTING : %s => %d status code " %(url,e.code))


                pass
     
def bruter_recursive(queue_words, new_target , extensions=None ):

        while not queue_words.empty():
            attempt = queue_words.get()
            attempt_list = []   

            #we control if the file has an ext
            # if not , it's a directory path
            
            if "." not in attempt :
                attempt_list.append("%s/" % attempt)
                if extensions :                         #if extensions are been declared, we add them to dir paths
                    for ext in extensions :
                        attempt_list.append("%s%s" % (attempt,ext)) 

            # we add extensions 
            else :                  
                attempt_list.append("%s"  % attempt)
                if extensions :
                    for ext in extensions :
                         if ext not in attempt :
                            string_no_ext = ".".join(attempt.split(".")[:-1])
                            attempt_list.append("%s%s" % (string_no_ext,ext))   

            for brute in attempt_list :

                url = "%s%s" %(new_target,urllib.parse.quote(brute)) #url parsing              

                try :
                    headers = {}
                    headers["User-Agent"] = user_agent
                    req = urllib.request.Request(url,headers=headers)   

                    response = urllib.request.urlopen(req)  

                    if len(response.read()) :
                        print ("%s => %d status code" %(url,response.code))
                        if ( response.code == 200 ) : #TODO: non inserire in lista gli url che puntano a file!!
                            if "." not in ( url.split("/")[-1] ) :
                                #print (f"Added to the recursive list: {url}")
                                recursive_list.append( url )
                            
                    
                except urllib.error.HTTPError as e :    

                    if (hasattr(e,'code') and e.code != 404)  : 
                        print ("COULD BE INTERESTING : %s => %d status code " %(url,e.code))    
    

                    pass

def run_threads(threads, queue_words, extensions):
    threads_list = []

    for x in range(threads):
        t = threading.Thread(target=bruter, args=(queue_words, extensions))
        threads_list.append(t)

    for th in threads_list:  # Avvio dei thread nella lista
        th.start()

    for th in threads_list:  # Attendiamo che tutti i thread terminino
        th.join()

def run_threads_recursive(threads, queue_words, new_target, extensions):
    threads_list = []

    for x in range(threads):
        t = threading.Thread(target=bruter_recursive, args=(queue_words, new_target , extensions ))
        threads_list.append(t)

    for th in threads_list:  
        th.start()

    for th in threads_list:  
        th.join()


print ( """

 ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌ ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌     ▐░▌          
▐░▌   ▄   ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌     ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ 
▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░▌       ▐░▌     ▐░▌     ▐░░░░░░░░░░░▌
▐░▌ ▐░▌░▌ ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀█░█▀▀ ▐░▌       ▐░▌     ▐░▌     ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌▐░▌ ▐░▌▐░▌▐░▌          ▐░▌       ▐░▌▐░▌     ▐░▌  ▐░▌       ▐░▌     ▐░▌     ▐░▌          
▐░▌░▌   ▐░▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░▌      ▐░▌ ▐░█▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ 
▐░░▌     ▐░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░▌ ▐░▌       ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌
 ▀▀       ▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀   ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀▀▀▀▀▀▀▀▀▀▀ 
                                                                                           
By Oiram98
 """)

settings() 
print("Starting directory brute forcing ...")
print(" ")
queue_words = initialize_wordlist(wordlist)
run_threads(threads, queue_words, extensions)
print (" ")

resume_from_here = None

if recursive:
    while len(recursive_list) != 0 : 
        new_target = recursive_list.pop()
        print(" ") 
        print( "--> Starting recursive brute forcing on: " + new_target + "\n")
        queue_words = initialize_wordlist(wordlist)
        run_threads_recursive(threads, queue_words, new_target, extensions)

print("")
print("Directory brute forcing completed !")
