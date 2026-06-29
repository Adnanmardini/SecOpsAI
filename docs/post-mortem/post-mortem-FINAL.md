DETECTION ENGINEER FINAL PROJECT LESSONS

The biggest thing I learned in this project is that security tools in the real world are much more difficult than they look in a classroom. On the 
first day I thought writing Suricata rules would be easy but I ran into a major wall with Suricata version 8. It was so strict that it would not 
even load my rules because I tried to check packet sizes and web data at the same time. I had to learn how to dig into the protocol logic and target 
specific ports like port 80 and port 53. This taught me that as a detection engineer you have to understand exactly how the engine is reading the 
traffic or your defenses will never even start.

I also learned a very important lesson about big data and computer memory. When I tried to run my Python script on the 2.5 million rows of data my 
terminal just said Killed and stopped working. I felt stuck for a moment but I learned that professional engineers do not just load everything at 
once. I had to learn how to process files one by one and change my data types from 64 bit to 32 bit to save RAM. I also used downsampling to keep 
all the hacker data but only a small amount of normal data. This was a huge win for me because it showed me how to work with massive datasets on a 
normal laptop without it crashing.

Working on the machine learning side opened my eyes to how hackers actually think. When I used the IBM ART library to attack our model I saw how 
easy it is to trick an AI with just a few small changes to the traffic. I learned that an AI is only as good as its training. By adding the hacker 
tricks back into the training data the model became much stronger and survived 4 out of 5 attacks. This taught me that you always have to act like a 
hacker to test your own defenses.

Finally I learned how critical it is to be synchronized with a team. There were times I was waiting for files or had to merge branches on GitHub and 
if our versions did not match the whole project would slow down. I had to re run my ablation study once I got the official files to make sure our 
final numbers were 100 percent correct for the client. Overall this project taught me that being a good engineer is not just about writing code but 
about solving technical problems as they happen and making sure every part of the system is documented so other people can understand it.
