# Database resources
# https://developer.hashicorp.com/terraform/language/providers

resource "aws_db_instance" "db" {
  tags = {
    Name        = "verusen-poc-db"
    Environment = "test"
  }
  identifier             = "verusen-poc-db"
  engine                 = "postgres"
  engine_version         = "14"
  instance_class         = "db.t3.micro"
  db_name                = "verusen"
  username               = "verusen"
  password               = "verusen123"
  allocated_storage      = 8
  apply_immediately      = true
  skip_final_snapshot    = true
  publicly_accessible    = true
  vpc_security_group_ids = [aws_security_group.db.id]
  backup_retention_period = 0
  deletion_protection = true
}

resource "aws_security_group" "db" {
  name        = "verusen-poc-db-sg"
  description = "Security group for verusen-poc-db database"

  ingress {
    description = "Allow external access to verusen-poc-db"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    // comment following lines to block any incoming external network requests
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "verusen-poc-db"
  }
}
