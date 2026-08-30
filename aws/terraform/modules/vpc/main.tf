# ==============================================================================
# AegisMesh VPC Module — 3-Tier Zero-Trust Network Architecture
# ==============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    {
      Name         = "${var.name_prefix}-vpc"
      ZeroTrust    = "Enforced"
      Architecture = "3-Tier-Multi-AZ"
    }
  )
}

# --- Internet Gateway (Public Web Tier Connectivity Only) ---
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-igw"
    }
  )
}

# --- Optional NAT Gateway (Cost Safety: Disabled by default) ---
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-nat-eip"
    }
  )
}

resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-nat-gw"
    }
  )

  depends_on = [aws_internet_gateway.igw]
}

# ==============================================================================
# Tier 1: Public Web Subnets (Ingress Load Balancers / Reverse Proxies)
# ==============================================================================
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index % length(var.availability_zones)]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name       = "${var.name_prefix}-public-subnet-${count.index + 1}"
      Tier       = "Public-Web"
      Zone       = "Untrusted-Edge"
      Compliance = "Zero-Trust-Tier-1"
    }
  )
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-public-rt"
      Tier = "Public-Web"
    }
  )
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ==============================================================================
# Tier 2: Private Application Subnets (Microservices / Backend API Engines)
# ==============================================================================
resource "aws_subnet" "private_app" {
  count                   = length(var.private_app_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_app_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index % length(var.availability_zones)]
  map_public_ip_on_launch = false

  tags = merge(
    var.tags,
    {
      Name       = "${var.name_prefix}-private-app-subnet-${count.index + 1}"
      Tier       = "Private-App"
      Zone       = "Internal-Services"
      Compliance = "Zero-Trust-Tier-2"
    }
  )
}

resource "aws_route_table" "private_app" {
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.nat[0].id
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-private-app-rt"
      Tier = "Private-App"
    }
  )
}

resource "aws_route_table_association" "private_app" {
  count          = length(aws_subnet.private_app)
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app.id
}

# ==============================================================================
# Tier 3: Isolated Database Subnets (Zero Internet Routing / RDS Tier)
# ==============================================================================
resource "aws_subnet" "isolated_db" {
  count                   = length(var.isolated_db_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.isolated_db_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index % length(var.availability_zones)]
  map_public_ip_on_launch = false

  tags = merge(
    var.tags,
    {
      Name       = "${var.name_prefix}-isolated-db-subnet-${count.index + 1}"
      Tier       = "Database-Isolated"
      Zone       = "Restricted-Data"
      Compliance = "Zero-Trust-Tier-3-AirGapped"
    }
  )
}

resource "aws_route_table" "isolated_db" {
  vpc_id = aws_vpc.main.id

  # STRICT ZERO-TRUST: No default 0.0.0.0/0 route to IGW or NAT.
  # Subnet only communicates with internal VPC routes.

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-isolated-db-rt"
      Tier = "Database-Isolated"
    }
  )
}

resource "aws_route_table_association" "isolated_db" {
  count          = length(aws_subnet.isolated_db)
  subnet_id      = aws_subnet.isolated_db[count.index].id
  route_table_id = aws_route_table.isolated_db.id
}

# --- Database Subnet Group (For AWS RDS PostgreSQL Microsegmentation) ---
resource "aws_db_subnet_group" "db_group" {
  name        = "${var.name_prefix}-db-subnet-group"
  description = "AegisMesh isolated database subnet group for Zero-Trust RDS deployment"
  subnet_ids  = aws_subnet.isolated_db[*].id

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-db-subnet-group"
      Tier = "Database-Isolated"
    }
  )
}
