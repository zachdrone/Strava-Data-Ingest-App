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
            "description": "Keep last 5 images",
            "selection": {
                "countType": "imageCountMoreThan",
                "countNumber": 5
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
