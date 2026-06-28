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
