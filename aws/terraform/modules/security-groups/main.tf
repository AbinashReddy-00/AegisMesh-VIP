# ==============================================================================
# AegisMesh Security Groups Module — Zero-Trust Stateful Microsegmentation
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Web Security Group (aegismesh-web-sg)
# Ingress: HTTPS 443 (and optional HTTP 80) from trusted CIDRs
# Egress: Application port strictly to aegismesh-app-sg; NO direct database egress
# ------------------------------------------------------------------------------
resource "aws_security_group" "web_sg" {
  name        = "${var.name_prefix}-web-sg"
  description = "AegisMesh Web Tier SG: Public Ingress (HTTPS) with Zero Database Access"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name      = "${var.name_prefix}-web-sg"
      Tier      = "Public-Web"
      ZeroTrust = "Ingress-Restricted"
    }
  )
}

resource "aws_security_group_rule" "web_ingress_https" {
  type              = "ingress"
  security_group_id = aws_security_group.web_sg.id
  description       = "Allow inbound HTTPS (443) from trusted web CIDRs"
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_blocks       = var.trusted_web_ingress_cidrs
}

resource "aws_security_group_rule" "web_ingress_http" {
  count             = var.enable_http ? 1 : 0
  type              = "ingress"
  security_group_id = aws_security_group.web_sg.id
  description       = "Allow inbound HTTP (80) if explicitly enabled"
  protocol          = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_blocks       = var.trusted_web_ingress_cidrs
}

resource "aws_security_group_rule" "web_egress_to_app" {
  type                     = "egress"
  security_group_id        = aws_security_group.web_sg.id
  description              = "Allow outbound traffic strictly to Application tier on app_port"
  protocol                 = "tcp"
  from_port                = var.app_port
  to_port                  = var.app_port
  source_security_group_id = aws_security_group.app_sg.id
}

# ------------------------------------------------------------------------------
# 2. Application Security Group (aegismesh-app-sg)
# Ingress: app_port strictly from aegismesh-web-sg (No direct public ingress)
# Egress: db_port strictly to aegismesh-db-sg
# ------------------------------------------------------------------------------
resource "aws_security_group" "app_sg" {
  name        = "${var.name_prefix}-app-sg"
  description = "AegisMesh App Tier SG: Ingress strictly from Web SG; Egress strictly to DB SG"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name      = "${var.name_prefix}-app-sg"
      Tier      = "Private-App"
      ZeroTrust = "Mutual-SG-Attested"
    }
  )
}

resource "aws_security_group_rule" "app_ingress_from_web" {
  type                     = "ingress"
  security_group_id        = aws_security_group.app_sg.id
  description              = "Allow inbound traffic strictly from Web Security Group on app_port"
  protocol                 = "tcp"
  from_port                = var.app_port
  to_port                  = var.app_port
  source_security_group_id = aws_security_group.web_sg.id
}

resource "aws_security_group_rule" "app_egress_to_db" {
  type                     = "egress"
  security_group_id        = aws_security_group.app_sg.id
  description              = "Allow outbound database traffic strictly to Database Security Group on db_port"
  protocol                 = "tcp"
  from_port                = var.db_port
  to_port                  = var.db_port
  source_security_group_id = aws_security_group.db_sg.id
}

# ------------------------------------------------------------------------------
# 3. Database Security Group (aegismesh-db-sg)
# Ingress: db_port strictly from aegismesh-app-sg
# Zero Direct Ingress from Web SG or public CIDRs (Air-Gapped Data Layer)
# Egress: Default Deny (no outbound internet or lateral egress)
# ------------------------------------------------------------------------------
resource "aws_security_group" "db_sg" {
  name        = "${var.name_prefix}-db-sg"
  description = "AegisMesh Database Tier SG: Ingress strictly from App SG; Zero Public/Web Access"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name      = "${var.name_prefix}-db-sg"
      Tier      = "Database-Isolated"
      ZeroTrust = "AirGapped-Restricted"
    }
  )
}

resource "aws_security_group_rule" "db_ingress_from_app" {
  type                     = "ingress"
  security_group_id        = aws_security_group.db_sg.id
  description              = "Allow inbound database connections strictly from Application Security Group"
  protocol                 = "tcp"
  from_port                = var.db_port
  to_port                  = var.db_port
  source_security_group_id = aws_security_group.app_sg.id
}
