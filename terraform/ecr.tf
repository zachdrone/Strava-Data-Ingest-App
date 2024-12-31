resource "aws_ecr_repository" "my_lambda_repo" {
  name = "my-lambda-repo"
}

resource "aws_ecr_lifecycle_policy" "my_lambda_repo_lifecycle" {
  repository = aws_ecr_repository.my_lambda_repo.name

  policy = <<EOF
  {
      "rules": [
          {
              "rulePriority": 1,
              "description": "Expire images older than 14 days",
              "selection": {
                  "tagStatus": "untagged",
                  "countType": "sinceImagePushed",
                  "countUnit": "days",
                  "countNumber": 14
              },
              "action": {
                  "type": "expire"
              }
          }
      ]
  }
  EOF
}
