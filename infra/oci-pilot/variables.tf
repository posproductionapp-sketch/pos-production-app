variable "region" {
  type    = string
  default = "ap-singapore-1"
}

variable "compartment_ocid" {
  type        = string
  description = "OCI compartment OCID where the Pilot resources will be created."
  sensitive   = true
}

variable "vcn_ocid" {
  type        = string
  description = "OCID of the existing manually-created prodx-pilot-vcn."
  sensitive   = true
}

variable "ssh_public_key" {
  type        = string
  description = "SSH public key installed on the Pilot VM."
  sensitive   = true
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "instance_name" {
  type    = string
  default = "prodx-pilot"
}

variable "ocpus" {
  type    = number
  default = 2
}

variable "memory_in_gbs" {
  type    = number
  default = 12
}
