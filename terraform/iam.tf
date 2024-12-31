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
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameters",
      "ssm:GetParameter",
      "ssm:DescribeParameters"
    ]

    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/encryption_key",
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/strava_callback_state",
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/strava_client_id",
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/strava_client_secret",
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/webhook_subscription_id",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "states:StartExecution"
    ]

    resources = [
      "arn:aws:states:${var.aws_region}:${data.aws_caller_identity.current.account_id}:stateMachine:process-strava-data",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]

    resources = [
      "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/users",
      "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/activities"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.strava_parquet_data_bucket.bucket}",
      "arn:aws:s3:::${aws_s3_bucket.strava_parquet_data_bucket.bucket}/*",
      "arn:aws:s3:::${aws_s3_bucket.strava_gpx_data_bucket.bucket}",
      "arn:aws:s3:::${aws_s3_bucket.strava_gpx_data_bucket.bucket}/*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.strava_activity_queue.arn,
      aws_sqs_queue.process_strava_data_trigger_dql.arn,
      aws_sqs_queue.delete_activity_queue.arn,
      aws_sqs_queue.delete_activity_queue_dlq.arn,
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

resource "aws_iam_role" "glue_execution_role" {
  name = "glue-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })
}

data "aws_iam_policy_document" "glue_policy_doc" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.strava_parquet_data_bucket.bucket}",
      "arn:aws:s3:::${aws_s3_bucket.strava_parquet_data_bucket.bucket}/*"
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

  statement {
    effect = "Allow"

    actions = [
      "glue:GetCrawler",
      "glue:StartCrawler",
      "glue:StopCrawler",
      "glue:GetCrawlerMetrics",
      "glue:GetTable",
      "glue:BatchCreatePartition",
      "glue:BatchDeletePartition",
      "glue:UpdatePartition",
      "glue:BatchGetPartition",
      "glue:CreateTable",
      "glue:GetTable",
      "glue:UpdateTable",
      "glue:DeleteTable",
      "glue:GetDatabase",
    ]

    resources = [
      "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:catalog",
      "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${aws_glue_catalog_database.strava_catalog_db.name}/*",
      aws_glue_catalog_database.strava_catalog_db.arn,
      aws_glue_crawler.strava_data_crawler.arn
    ]
  }
}

resource "aws_iam_policy" "glue_policy" {
  name   = "glue_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.glue_policy_doc.json
}

resource "aws_iam_policy_attachment" "glue_policy_attachment" {
  name       = "glue-policy-attachment"
  policy_arn = resource.aws_iam_policy.glue_policy.arn
  roles      = [aws_iam_role.glue_execution_role.name]
}

resource "aws_iam_role" "eventbridge_sfn_role" {
  name = "eventbridge-sfn-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "events.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "eventbridge_sfn_policy" {
  name = "eventbridge-sfn-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "states:StartExecution"
      ],
      Resource = aws_sfn_state_machine.process_strava_data.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eventbridge_sfn_attach" {
  role       = aws_iam_role.eventbridge_sfn_role.name
  policy_arn = aws_iam_policy.eventbridge_sfn_policy.arn
}

resource "aws_iam_role" "step_function_role" {
  name = "stepFunctionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "step_function_policy" {
  name        = "stepFunctionPolicy"
  description = "Policy to allow execution of Lambda"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action   = "lambda:InvokeFunction",
      Effect   = "Allow",
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "step_function_policy_attach" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_policy.arn
}
