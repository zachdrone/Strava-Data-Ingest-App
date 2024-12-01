resource "aws_lambda_function" "health_endpoint" {
  function_name = "health_endpoint"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "src.lambdas.health.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "callback_endpoint" {
  function_name = "callback_endpoint"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "src.lambdas.callback.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "webhook_endpoint" {
  function_name = "webhook_endpoint"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      ACTIVITY_QUEUE_URL = aws_sqs_queue.strava_activity_queue.url
      handler            = "src.lambdas.webhook.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "process_strava_data" {
  function_name = "process_strava_data"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      ACTIVITY_QUEUE_URL = aws_sqs_queue.strava_activity_queue.url
      S3_BUCKET          = aws_s3_bucket.strava_data_bucket.bucket
      handler            = "src.lambdas.process_strava_data.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}
