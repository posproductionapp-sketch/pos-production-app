# PRODX Pilot — OCI Infrastructure

This directory defines the Pilot infrastructure as code. It is intentionally separate from the certified application code.

## What it creates

- OCI VCN `prodx-pilot-vcn` (`10.0.0.0/16`)
- Internet Gateway
- Public route table with `0.0.0.0/0` to the Internet Gateway
- Public subnet `10.0.1.0/24`
- Security list exposing only TCP 22, 80 and 443
- Always Free eligible ARM compute shape `VM.Standard.A1.Flex` at 2 OCPU / 12 GB RAM
- Ubuntu 24.04 ARM image selected dynamically
- Docker Engine + Compose plugin bootstrap

PostgreSQL and Redis are **not exposed to the Internet**. They remain application-internal services on the Docker network defined by the existing production compose configuration.

## Authentication

Use OCI API-key credentials through Terraform variables or a secure CI secret store. Never commit OCI private keys, SSH private keys, database passwords, or application secrets.

## Apply

Run from a trusted machine or OCI Resource Manager after supplying:

- `tenancy_ocid`
- `user_ocid`
- `fingerprint`
- `private_key_path`
- `compartment_ocid`
- `ssh_public_key`

Then:

```text
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

The first apply creates the complete network + VM. Subsequent applies reconcile drift instead of requiring manual console work.

## Existing manually-created VCN

The first Pilot VCN was created manually during initial setup. Do **not** point this configuration at it without importing its resources into Terraform state. The safe options are:

1. destroy the unused manual Pilot VCN and let Terraform create the managed Pilot stack; or
2. import each existing resource into this Terraform state before applying.

Do not create duplicate VCNs, subnets, gateways or instances accidentally.
