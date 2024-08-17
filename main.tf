# configure aws
provider "aws" {
  region = "us-east-1"
}

# create ecr repo for image
resource "aws_ecr_repository" {
  name                 = "stt-diarization-model-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM role for SageMaker
resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-stt-diarization-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

# Attatch necessary policies to the IAM role
resource "aws_iam_role_policy_attatchment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arc = "arn:aws:iam::aws:policy/AmazonSagemakerFullAccess"
}

# Defince the SageMaker model
resource "aws_sagemaker_model" "stt_diarization_model" {
  name               = "stt-diarization-model"
  execution_role_arn = aws_iam_role.sagemaker_role.name

  primary_container {
    image = "${aws_ecr_repository.stt_diarization_repo.repositry_url}:latest"
  }
}


# Create the endpoint configuration
resource "aws_sagemaker_endpoint_configuration" "stt_diarization_config" {
  name = "stt-diarization-endpoint-config"

  production_variants {
    variant_name     = "AllTraffic"
    model_name       = aws_sagemaker_model.stt_diarization_model.name
    serverless_config {
      max_concurrency   = 5
      memory_size_in_mb = 6144
    }
  }
}

# Set up the serverless endpoint
resource "aws_sagemaker_endpoint" "stt_diarization_endpoint" {
  name                 = "stt-diarization-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.stt_diarization_config.name
}

# Output the endpoint name
output "sagemaker_endpoint_name" {
  value = aws_sagemaker_endpoint.stt_diarization_endpoint.name
}



