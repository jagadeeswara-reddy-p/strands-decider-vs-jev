terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project   = "strands-decider-eval"
      ManagedBy = "terraform"
    }
  }
}

# Latest Deep Learning Base AMI (NVIDIA driver + CUDA preinstalled), resolved via the public SSM parameter.
data "aws_ssm_parameter" "dlami" {
  name = "/aws/service/deeplearning/ami/x86_64/base-oss-nvidia-driver-gpu-ubuntu-22.04/latest/ami-id"
}

data "aws_vpc" "default" {
  default = true
}

# ---------------------------------------------------------------- access: SSM only, no inbound ports

resource "aws_iam_role" "decider" {
  name_prefix = "strands-decider-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.decider.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "decider" {
  name_prefix = "strands-decider-"
  role        = aws_iam_role.decider.name
}

resource "aws_security_group" "decider" {
  name_prefix = "strands-decider-"
  description = "strands-decider eval: egress only, access via SSM port forwarding"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------------------------------------------- the GPU box

resource "aws_instance" "decider" {
  ami                    = data.aws_ssm_parameter.dlami.insecure_value
  instance_type          = var.instance_type
  iam_instance_profile   = aws_iam_instance_profile.decider.name
  vpc_security_group_ids = [aws_security_group.decider.id]

  # Cost guard: an autostop unit shuts down after each boot; shutdown means stop, so the cached model survives.
  instance_initiated_shutdown_behavior = "stop"

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    volume_size           = var.root_volume_gb
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    checkpoint        = var.checkpoint
    port              = var.port
    packages          = var.packages
    auto_stop_minutes = var.auto_stop_minutes
  })
  # false: editing user_data must not silently replace the box; apply such changes over SSM instead.
  user_data_replace_on_change = false

  tags = {
    Name = "strands-decider-eval"
  }
}
