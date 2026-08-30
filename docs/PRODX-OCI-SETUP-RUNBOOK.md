# PRODX OCI Setup Runbook

Status: active production setup record  
Region: `ap-singapore-1`

## Purpose

Record the repeatable OCI/Cloud Shell configuration method used for PRODX so infrastructure work does not depend on ad-hoc commands or repeated manual recovery.

## Configuration principles

1. Inspect existing resources before creating anything.
2. Reuse existing OCIDs through shell variables after verified lookup.
3. Fail fast when a required OCID is empty; never continue and report success.
4. Verify every resource after mutation.
5. Prefer OCI CLI JMESPath output over brittle `jq`/shell escaping.
6. Never store tenancy secrets, API keys, passwords, private keys, or database credentials in this repository.
7. Keep database resources private and restrict access through security rules/NSGs.
8. Treat `SETUP COMPLETE` as valid only after explicit final verification succeeds.
9. If Cloud Shell reconnects and variables disappear, re-query OCI; never create duplicates just because a variable is empty.

## Verified network foundation

- VCN: `prodx-pilot-vcn`
- VCN CIDR: `10.0.0.0/16`
- Internet Gateway: `prodx-pilot-igw`
- Internet Gateway state: `AVAILABLE`
- Internet Gateway enabled: `true`
- Public subnet: `prodx-pilot-public-subnet`
- Public subnet CIDR: `10.0.10.0/24`
- Public subnet state: `AVAILABLE`
- OCI region: `ap-singapore-1`

## Repeatable lookup pattern

```bash
export OCI_REGION="ap-singapore-1"

VCN_ID="$(oci network vcn list \
  --compartment-id "$OCI_TENANCY" \
  --region "$OCI_REGION" \
  --display-name "prodx-pilot-vcn" \
  --query 'data[0].id' \
  --raw-output)"

RT_ID="$(oci network vcn get \
  --vcn-id "$VCN_ID" \
  --region "$OCI_REGION" \
  --query 'data."default-route-table-id"' \
  --raw-output)"

IGW_ID="$(oci network internet-gateway list \
  --compartment-id "$OCI_TENANCY" \
  --vcn-id "$VCN_ID" \
  --region "$OCI_REGION" \
  --display-name "prodx-pilot-igw" \
  --query 'data[0].id' \
  --raw-output)"

if [ -z "$VCN_ID" ] || [ -z "$RT_ID" ] || [ -z "$IGW_ID" ]; then
  echo "ERROR: required OCI resource ID is missing"
  exit 1
fi
```

## Network sequence

`VCN -> Internet Gateway -> Default Route Table -> 0.0.0.0/0 route -> Public Subnet -> verification`

The public subnet uses `10.0.10.0/24`. Database infrastructure must not be placed in this public subnet.

## Recovery rule

When a Cloud Shell session reconnects, start from resource discovery rather than stale variables. Validate all IDs before mutation. Do not report completion unless final verification succeeds.

## Next infrastructure gate

Network Foundation is complete. The next gate is:

`Private DB subnet -> NSG/security rules -> managed PostgreSQL -> compute/app connectivity -> deployment verification`

All subsequent gates must preserve PRODX requirements for security-by-default, tenant isolation, financial integrity, auditability, idempotency, and production verification.
