
# README

## Environment Variables Reference

| Variable | Used by | Default | Notes |
| -- | -- | -- | -- |
| STAGING_AIRFLOW_API_VERSION | Staging Promotion | 2 | The Airflow Version for the Staging Environment \n For Airflow 2 = API v1 + Basic auth, Airflow 3 = API v2 + JWT |
| PRODUCTION_AIRFLOW_API_VERSION | Production Promotion | 2 | Same as above |
| AIRFLOW_JWT_SECRET | Any Promotion step that uses Airflow 3 | none | Must match the secret the Airflow 3 deployment signs with. Can be found in Secrets Manager |
| AIRFLOW_JWT_SUB | Airflow 3 only | none | The subject claim for the token (the Integer ID from Airflow's user table) |
