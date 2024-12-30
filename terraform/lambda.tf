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
      ACTIVITY_QUEUE_URL        = aws_sqs_queue.strava_activity_queue.url
      DELETE_ACTIVITY_QUEUE_URL = aws_sqs_queue.delete_activity_queue.url
      handler                   = "src.lambdas.webhook.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "process_strava_data_trigger" {
  function_name = "process_strava_data_trigger"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.process_strava_data.arn
      handler           = "src.lambdas.process_strava_data_trigger.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30

  dead_letter_config {
    target_arn = aws_sqs_queue.process_strava_data_trigger_dql.arn
  }
}

resource "aws_lambda_event_source_mapping" "process_strava_data_sqs_trigger" {
  event_source_arn = aws_sqs_queue.strava_activity_queue.arn
  function_name    = aws_lambda_function.process_strava_data_trigger.arn
  enabled          = true
}

resource "aws_lambda_function_event_invoke_config" "process_strava_data_trigger_config" {
  function_name                = aws_lambda_function.process_strava_data_trigger.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}

resource "aws_lambda_function" "prepare_and_upload_gpx" {
  function_name = "prepare_and_upload_gpx"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      GPX_DATA_BUCKET = aws_s3_bucket.strava_gpx_data_bucket.bucket
      handler         = "src.lambdas.prepare_and_upload_gpx.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "store_activity_in_dynamo" {
  function_name = "store_activity_in_dynamo"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "src.lambdas.store_activity_in_dynamo.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "check_child_users" {
  function_name = "check_child_users"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "src.lambdas.check_child_users.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "validate_child" {
  function_name = "validate_child"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "src.lambdas.validate_child.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "duplicate_activity" {
  function_name = "duplicate_activity"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      GPX_DATA_BUCKET = aws_s3_bucket.strava_gpx_data_bucket.bucket
      handler         = "src.lambdas.duplicate_activity.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "check_duplication_status" {
  function_name = "check_duplication_status"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      handler = "src.lambdas.check_duplication_status.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_function" "delete_activity" {
  function_name = "delete_activity"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_lambda_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      GPX_DATA_BUCKET     = aws_s3_bucket.strava_gpx_data_bucket.bucket
      PARQUET_DATA_BUCKET = aws_s3_bucket.strava_data_bucket.bucket
      handler             = "src.lambdas.delete_activity.handler.lambda_handler"
    }
  }

  memory_size = 512
  timeout     = 30
}

resource "aws_lambda_event_source_mapping" "delete_activity_sqs_trigger" {
  event_source_arn = aws_sqs_queue.delete_activity_queue.arn
  function_name    = aws_lambda_function.delete_activity.arn
  enabled          = true
}

resource "aws_lambda_function_event_invoke_config" "delete_activity_config" {
  function_name                = aws_lambda_function.delete_activity.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}
