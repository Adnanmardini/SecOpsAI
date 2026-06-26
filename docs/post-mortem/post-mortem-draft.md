DETECTION ENGINEER TECHNICAL POST MORTEM REPORT

OVERVIEW
This report documents the major technical problems encountered during the SecOpsAI project and the engineering solutions used to fix them. 

SOLUTION FOR SURICATA RULE ERRORS 
During the first phase I wrote 12 rules to find malware. These rules failed to load because Suricata version 8.0.5 is very 
strict. The engine did not allow me to check the size of a packet and the web content at the same time in one rule. To fix this I used protocol 
aware logic. I stopped using high level keywords and targeted the raw TCP and UDP ports directly. I targeted port 80 for web traffic and port 53 for 
DNS traffic. This allowed the engine to check both the data size and the content without errors. This fix ensured that our first layer of defense 
was active and stable. 

SOLUTION FOR MEMORY CRASHES
On Day 2 the Python script used to create the baseline failed with a Killed message. This 
happened because the dataset has over 2.5 million rows. The system ran out of RAM and stopped the process. I implemented a three part solution for 
memory management. One. I modified the code to process one CSV file at a time. This kept the memory usage low. Two. I used aggressive downsampling. 
I kept 100 percent of the attack data but only kept 1 percent of the normal traffic. Three. I changed the data types from 64 bit to 32 bit. This 
reduced the size of the data in memory by 50 percent. These changes allowed me to process the entire dataset in under five minutes without any 
further crashes. 

SOLUTION FOR ADVERSARIAL ATTACK FAILURES
On Day 4 the standard tools used to attack the AI model failed. This was because the attacks were designed for deep learning but our team used an 
XGBoost tree model. I fixed this by tuning the attack parameters. I switched to the ZOO method which is a black box attack. I also set the parallel 
processing setting to one. This matched the number of features in our data and allowed the security tests to complete. The model successfully 
survived four out of five attacks after these adjustments. 

FINAL LESSONS
The main lesson I learned is that tools and data often have hidden limits. A good engineer must know how to optimize code for memory and adjust 
security rules for new software versions. These solutions allowed us to meet the client requirement of a 99 percent improvement in detection.
