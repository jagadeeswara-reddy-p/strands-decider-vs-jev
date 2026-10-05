output "instance_id" {
  value = aws_instance.decider.id
}

output "ami_id" {
  value = aws_instance.decider.ami
}

output "port_forward_command" {
  description = "Run locally, then the decider is at http://127.0.0.1:<port>"
  value       = "aws ssm start-session --region ${var.region} --target ${aws_instance.decider.id} --document-name AWS-StartPortForwardingSession --parameters portNumber=${var.port},localPortNumber=${var.port}"
}

output "logs_command" {
  value = "aws ssm start-session --region ${var.region} --target ${aws_instance.decider.id}   # then: sudo journalctl -u strands-decider -f"
}
