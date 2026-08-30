output "instance_id" {
  value = oci_core_instance.pilot.id
}

output "public_ip" {
  value = oci_core_instance.pilot.public_ip
}

output "vcn_id" {
  value = oci_core_vcn.pilot.id
}

output "public_subnet_id" {
  value = oci_core_subnet.public.id
}
