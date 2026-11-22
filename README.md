# NZ DevOps Azure Hands-on Lab (21 days)

This is a **personal demo project**, NOT a claim of workplace production experience. No bank/customer data, company source code, credentials or internal documents should be used.

## Architecture target (at the end of the programme)

GitHub PR -> GitHub Actions (test, build, security checks) -> container image -> Azure Container Apps (DEV/TEST) -> Azure Monitor / Log Analytics. Terraform manages selected Azure resources. Use Microsoft Entra workload federation (OIDC) to authenticate deployment pipelines without long-lived Azure secrets.

The starter only includes the local app, test suite, Dockerfile, CI workflow, and a safe introductory Terraform network configuration. Cloud deployment, environment approvals, monitoring and policies are **future labs**, intentionally not preimplemented.

## Day 1: Azure identity, subscription and resource groups

1. Sign in to https://portal.azure.com with a **personal** Microsoft account and a subscription you control. If you're eligible for a free account, review its terms. Set budget alerts before deploying paid resources. **Budget alerts do not automatically stop spending.**
2. Open Azure Cloud Shell (Bash) from the portal. No local Azure CLI installation is needed for this first lab.
3. Run:

```bash
az account show --query '{subscription:id,name:name,tenant:tenantId}' -o json
az account list-locations --query "[?name=='newzealandnorth'].{Region:name,DisplayName:displayName}" -o table
az group create --name rg-nzdevops-sandbox --location newzealandnorth --tags project=nzdevops-lab environment=sandbox
az group show --name rg-nzdevops-sandbox --query '{name:name,location:location,tags:tags}' -o json
az group list --query "[?tags.project=='nzdevops-lab'].{name:name,location:location}" -o table
```

4. In the portal inspect Activity Log, IAM (Access Control) and Tags for the new resource group. Do not use real credentials in screenshots.
5. After saving notes, remove this **sandbox** group (do not delete other resource groups):

```bash
az group delete --name rg-nzdevops-sandbox --yes
```

6. Interview prompt: "What is the difference between tenant, subscription, resource group and region, and how would you control access and cost?"

## Day 2: Run the API locally

Requires Python 3.12+ and optional Docker Desktop. From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux; on Windows use .venv\\Scripts\\activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
uvicorn app.main:app --reload --port 8080
```

In another terminal:

```bash
curl -i http://127.0.0.1:8080/health/live
curl -i http://127.0.0.1:8080/health/ready
curl -i http://127.0.0.1:8080/api/v1/transactions/demo-001
curl -i http://127.0.0.1:8080/api/v1/transactions/unknown
```

**Failure drill** (after stopping the first server):

```bash
SIMULATE_OUTAGE=true uvicorn app.main:app --port 8080
curl -i http://127.0.0.1:8080/health/ready  # should be HTTP 503
```

Questions: What is the difference between liveness and readiness? How would orchestration react to these signals? Why should application logs omit credentials and personal data?

## Day 3: Container exercise

```bash
docker build -t nz-devops-lab:v1 .
docker run --rm -p 8080:8080 nz-devops-lab:v1
# In another terminal: curl -i http://127.0.0.1:8080/health/live
```

Break it on purpose and debug with `docker logs`, `docker ps`, `docker inspect`. Try stopping the container and restarting with `-e SIMULATE_OUTAGE=true`.

## Days 4-5: Git and CI

1. Make a new **private or public personal** GitHub repository, not a company repository.
2. Commit the project on `main`. Open a branch, make a small test change, and raise a PR.
3. Inspect `.github/workflows/ci.yml`. Confirm the PR executes unit tests and a Docker build.
4. Deliberately break an assertion and verify the pipeline fails. Fix it in a follow-up commit.
5. For production systems, assess actions SHA-pinning, dependency scanning and restricted workflow permissions.

## Days 6-8: Terraform foundations

This lab creates a resource group, VNet and subnet. Terraform uses the Azure CLI credentials in your **personal** subscription. Always inspect `terraform plan` before apply. Verify region availability in your subscription.

```bash
az login
export TF_VAR_subscription_id="$(az account show --query id -o tsv)"
cd infra
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform output
terraform plan               # should show no changes if there's no drift
terraform destroy            # after recording evidence; confirm the target is your lab
```

Do not commit subscription IDs, state files, `.tfvars`, keys or credentials. Later, learn remote Terraform state, locking, RBAC and drift management.

## Later hands-on modules (Days 9-21)

- Day 9: Azure Storage, blob access controls, encryption, and cost review
- Day 10: Azure Container Apps deployment and endpoint verification
- Day 11: Pipeline-to-Azure federated identity (OIDC); least-privilege deployment
- Day 12: Application changes -> CI -> release to DEV; smoke test
- Day 13: TEST environment, reviews, manual approvals and rollback
- Day 14: Troubleshooting practice: failed builds, wrong env vars, failed deployment
- Day 15: Build analogous Azure DevOps YAML pipeline; understand service connections
- Day 16: Azure Monitor, Log Analytics, alerting and a documented incident
- Day 17: kind/minikube local Kubernetes (Deployment, Service, readiness/liveness)
- Day 18: Helm and configuration per environment; avoid costly AKS by default
- Day 19: RBAC, managed identity, Key Vault architecture and security review
- Day 20: AZ-104 official practice assessment; targeted weak-topic labs
- Day 21: Architecture walkthrough, incident story, repo/README portfolio and mock technical interview

## Cost safety

Many Azure services charge even when idle; budget alerts are NOT hard caps. Start with free/trial-eligible services when appropriate, use scale-to-zero where supported, minimise log retention and network egress, delete individual labs after use, and review Azure Cost Management daily. AKS, VMs, public IPs, container registries, monitoring workspaces and networking add-ons may incur charges.

## How to ask for help

After each day, send: (1) what commands you ran, (2) output or error **with secrets and IDs masked**, (3) what you think happened. Ask for "Day 2" after Day 1. We'll troubleshoot and do interview questions based on what you actually built.
# azure-devops-transaction-api
