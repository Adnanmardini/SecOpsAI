# Post-Mortem Contribution (DevOps & Infrastructure)
# Sub-Team 2 – DevOps Engineer (Peter)


During the infrastructure validation phase, the Docker environment was successfully stabilized and verified before the final demonstration. Several deployment issues were identified and resolved, including Docker Compose path inconsistencies, Kafka topic initialization, API verification, and container startup behaviour.

Key Contributions
Updated Docker Compose configuration to reflect the correct project structure.
Verified successful cold-start of all project containers.
Confirmed API authentication and RBAC functionality.
Verified PostgreSQL, Redis, Kafka, Prometheus and Grafana startup.
Created a reusable Kafka topic setup script for consistent environment initialization.
Documented infrastructure setup and deployment procedures.
Lessons Learned
Docker service paths should remain consistent across all branches to avoid build failures.
Kafka topics should be initialized automatically during project setup rather than manually after every deployment.
Infrastructure validation should always be completed before application-level testing begins.
Small configuration differences between branches can introduce deployment failures even when application code is correct.

Recommendations
Standardize a single Docker Compose file across all development branches.
Automate Kafka topic creation during deployment.
Include infrastructure smoke tests as part of the deployment checklist.
Maintain deployment documentation alongside infrastructure changes.
