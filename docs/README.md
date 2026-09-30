# README

The workflows read config from two GitHub Environments (under Settings -> Environments): `staging` and `production`. A job only sees the secrets and vars of the environment it declares. The same secret name, therefore, can hold a different value in each stage.

## Which workflow uses which environment

- `staging` is used by [pr.yml](../.github/workflows/pr.yml). It runs when a PR is opened or updated and publishes to staging Airflow.
- `production` is used by [promote.yml](../.github/workflows/promote.yml) which [promotion-checker.yml](../.github/workflows/promotion-checker.yml) triggers after the PR is approved. It publishes to production Airflow.

For the GitHub `staging` environment, the following config should be set:

- Secrets, for a staging instance using Airflow 2, `STAGING_SM2A_ADMIN_USERNAME` and `STAGING_SM2A_ADMIN_PASSWORD`.
- Secrets, for a staging instance using Airflow 3, `AIRFLOW_JWT_SECRET` and `AIRFLOW_JWT_SUB`.
- Secret for the MDX PR step: `APP_PEM`.
- Vars: `STAGING_SM2A_API_URL`, `STAGING_AIRFLOW_API_VERSION`, `DATASET_DAG_NAME`, and `ARTIFACT_RETENTION_DAYS`.
- Vars for the MDX step: `SKIP_MDX_PR_STEP`, `VEDA_CONFIG_REPO_ORG`, `VEDA_CONFIG_REPO_NAME`, `VEDA_CONFIG_APP_ID`, and `GH_ACTOR_EMAIL`.

For the GitHub `production` environment, the following config should be set:

- Secrets, for a production instance using Airflow 2, `SM2A_ADMIN_USERNAME` and `SM2A_ADMIN_PASSWORD`.
- Secrets, for a production instance using Airflow 3, `AIRFLOW_JWT_SECRET` and `AIRFLOW_JWT_SUB` *which should be different values from what is set in staging*.
- Vars: `SM2A_API_URL`, `PRODUCTION_AIRFLOW_API_VERSION` and `PROMOTION_DAG_NAME`.

> Note: `*_AIRFLOW_API_VERSION` is the Airflow major version (can be either 2 or 3) which defaults to 2 if unset. The JWT secrets **are only needed for Airflow 3**.

### Repo-level secrets

Set repo level secrets under `Settings` -> `Secrets and variables` -> `Actions`.

- `WORKFLOW_TRIGGER_TOKEN` which is a repo-level secret that isn't environment scoped. It is required for `promote.yml`.

## Environment Variables Reference for Collection and Dataset Promotion

> See the [terminology note](../README.md#step-4-promote-to-production) in the root README for what "promotion" implies.
>

| Variable | Set in | Used by | Default | Notes |
| -- | -- | -- | -- | -- |
| STAGING_AIRFLOW_API_VERSION | Staging GitHub Env | Staging Publish/Promotion | 2 | The Airflow Version for the Staging Environment.  For Airflow 2 = API v1 + Basic auth, Airflow 3 = API v2 + JWT |
| PRODUCTION_AIRFLOW_API_VERSION | Production GitHub Env | Production Promotion | 2 | Same as above |
| AIRFLOW_JWT_SECRET | Both (optional) | Any Publish/Promotion step that uses Airflow 3 | none | Conditionally required when the resolved API version is 3. Must match the secret that the Airflow 3 deployment signs with. Can be found in Secrets Manager |
| AIRFLOW_JWT_SUB | Both (optional) | Airflow 3 only | none | Conditionally required when the resolved API version is 3. The subject claim for the token (the Integer ID from Airflow's user table) |
