resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    effect = "Allow"
    
    actions = [
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds"
    ]

    resources = [
      "arn:aws:secretsmanager:us-east-1:${data.aws_caller_identity.current.account_id}:secret:strava_app-8ZESlw"
    ]
  }

  statement {
    effect = "Allow"
    
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "lambda_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

resource "aws_iam_policy_attachment" "lambda_policy_attachment" {
  name       = "lambda-policy-attachment"
  policy_arn = resource.aws_iam_policy.lambda_policy.arn
  roles      = [aws_iam_role.lambda_execution_role.name]
}