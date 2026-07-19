<<<<<<< HEAD
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
=======
# SecOpsAI Project Post-Mortem

## Security Analyst Lesson — Denise Sophy

Working as the Security Analyst on Sub-Team 4 taught me that building a security 
operations pipeline is as much about infrastructure coordination as it is about writing 
code. My alert consumer, email notifier, and traffic generator scripts all worked 
correctly in isolation, but integrating them with Kafka and Grafana exposed how dependent 
each component is on the others.

The biggest lesson was the importance of testing dependencies early. Kafka's Zookeeper 
connectivity issue blocked my Grafana dashboard verification task for several days. In 
future projects I would establish a shared working environment at the start so all team 
members can test against the same infrastructure rather than running separate local 
instances.

I also learned the value of documenting blockers clearly and promptly. Rather than 
waiting for the infrastructure to be fixed, I committed my scripts and documented exactly 
what was blocking me and what was needed to unblock it. This kept the project moving and 
made it clear my deliverables were complete even when the full end-to-end test could not 
run.
>>>>>>> origin/team-4-redteam-response
