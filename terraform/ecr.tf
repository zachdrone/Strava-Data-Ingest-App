resource "aws_ecr_repository" "my_lambda_repo" {
  name                 = "my-lambda-repo"
  image_tag_mutability = "IMMUTABLE"
}

resource "aws_ecr_repository" "my_lambda_repo_cache" {
  name = "my-lambda-repo-cache"
}

resource "aws_ecr_lifecycle_policy" "my_lambda_repo_lifecycle" {
  repository = aws_ecr_repository.my_lambda_repo.name

  policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire images older than 3 days except the latest 3",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 3,
        "countUnit": "days",
        "countValue": 3
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Keep only the latest image after 3 days",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}

EOF
}

resource "aws_ecr_lifecycle_policy" "my_lambda_repo_lifecycle_cache" {
  repository = aws_ecr_repository.my_lambda_repo_cache.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep last 1 images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}
