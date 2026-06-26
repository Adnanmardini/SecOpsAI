Last updated: June 26, 2026

## Schema Overview (6 Tables) 
| Table | Purpose | Row Count (approx) | Key Constraint | 
|---|---|---|---| 
| users | Authentication | Small (team members only) | Unique username | 
| network_flows | Raw telemetry | Large (millions) | SHA-256 integrity hash | 
| detection_results | ML predictions | Large | FK to network_flows | 
| security_alerts | Enriched alerts | Medium | FK to detection_results | 
| audit_log | Tamper-evident log | Large | Hash chain, no-delete rule | 
| model_versions | ML model registry | Small | Unique mlflow_run_id | 
 
## Tamper-Evident Audit Log 
 
The audit_log table is append-only. Deletion is blocked by a PostgreSQL rule: 
```sql 
CREATE RULE audit_log_no_delete AS 
    ON DELETE TO audit_log DO INSTEAD NOTHING; 
 
Hash-chain verification: 
WITH chain_check AS ( 
    SELECT id, entry_hash, 
           LAG(entry_hash) OVER (ORDER BY id) as expected_prev 
    FROM audit_log 
) 
SELECT id, 
       CASE WHEN id = 1 OR prev_entry_hash = expected_prev 
            THEN 'INTACT' 
            ELSE 'BROKEN' 
       END as status 
FROM chain_check 
ORDER BY id;
