output "web_security_group_id" {
  description = "The ID of the Web tier security group"
  value       = aws_security_group.web_sg.id
}

output "app_security_group_id" {
  description = "The ID of the Application tier security group"
  value       = aws_security_group.app_sg.id
}

output "db_security_group_id" {
  description = "The ID of the Database tier security group"
  value       = aws_security_group.db_sg.id
}
