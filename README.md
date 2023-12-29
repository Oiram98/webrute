# webrute
Web app directories and files enumeration tool

I experienced some problems using other blasoned tools especially when I utilized them with proxychains, so I decided to write my own tool for directory discovering. 

I present to you Webrute ! 

At the moment the tool allows you:

<ul>
  <li> performing directory/files discover specifying any wordlist   </li>
  <li> Starting the directory brute forcing at a specific point of the wordlist  </li>
  <li> specifying the number of the threads for the directory brute forcing </li>
  <li> specifying the extensions that will be added to the wordlist entries that no have extensions  </li>
  <li> specifying the number of the threads for the directory brute forcing </li>
  <li> Filtering out the results by response code number </li>
  <li> performing recursive directory brute forcing ( only for those path getting response status code 200 ) </li>
</ul>


The tool could be improved in the future. If you found this project interesting and would like to support me:

https://paypal.me/coffee4Oiram 

![alt text](https://github.com/Oiram98/webrute/blob/main/test_webrute.png?raw=true)


NOTES.

<ul>
  <li>To know how webrute works you can issues this command : python3 webrute.py -h</li>
  <li>You can download the wordlist to test webrute from this repository . Please ,
  make sure to insert wordlist.txt in /tmp path if you want run webrute with default settings</li>
  <li>Webrute works for http (mostly) and https websites</li>
  <li>The author is not responsible for the use of the "webrute" tool by third-party people</li>
</ul>

VERSIONS.

v1.0  

v2.0  fix bugs, better user experience, added recursive directory brute forcing

v3.0 (current) fix minor bugs, added filtering and banner skipping






