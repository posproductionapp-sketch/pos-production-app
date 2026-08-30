# PRODX Pilot — OCI Infrastructure

This directory defines the Pilot infrastructure as code. It is intentionally separate from the certified application code.

## What it creates

- Reuses the existing OCI VCN `prodx-pilot-vcn` (`10.0.0.0/16`)
- Internet Gateway
- Public route table with `0.0.0.0/0` to the Internet Gateway
- Public subnet `10.0.1.0/24`
- Security list exposing only TCP 22, 80 and 443
- Always Free eligible ARM compute shape `VM.Standard.A1.Flex` at 2 OCPU / 12 GB RAM
- Ubuntu 24.04 ARM image selected dynamically
- Docker Engine + Compose plugin bootstrap

PostgreSQL and Redis are **not exposed to the Internet**. They remain application-internal services on the Docker network defined by the application deployment.

## OCI Resource Manager

The preferred deployment path is OCI Resource Manager. Resource Manager provides Terraform state management and runs Plan/Apply jobs without requiring OCI API credentials or private keys to be committed to the repository.

Set these stack variables:

- `region` = `ap-singapore-1`
- `compartment_ocid`
- `vcn_ocid` = OCID of the existing `prodx-pilot-vcn`
- `ssh_public_key`

Keep all OCIDs and keys out of source control unless they are explicitly non-secret identifiers. Never commit OCI private keys, SSH private keys, database passwords, or application secrets.

## Deployment flow

1. Create a Resource Manager stack from this directory (GitHub source is preferred).
2. Enter the four variables above.
3. Run **Plan** and verify the plan only creates the Internet Gateway, route table, security list, public subnet, and Pilot VM against the existing VCN.
4. Run **Apply**.
5. Confirm the Terraform outputs for the instance ID, public IP, VCN ID, and public subnet ID.
6. Run the Pilot smoke/health checks before treating the environment as usable.

The existing VCN is intentionally referenced as a data source. Terraform will not attempt to recreate or replace it.

## Local Terraform

For local Terraform, use the OCI provider's supported environment/config authentication rather than storing credentials in `.tf` files. Then run:

```text
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

Subsequent applies reconcile drift instead of requiring manual console work.
