resource "aws_sqs_queue" "strava_activity_queue" {
  name = "strava-activity-queue"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.strava_activity_queue_dlq.arn
    maxReceiveCount     = 1
  })
}

resource "aws_sqs_queue" "strava_activity_queue_dlq" {
  name = "strava-activity-queue-dlq"
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.strava_activity_queue.arn
  function_name    = aws_lambda_function.process_strava_data.arn
  enabled          = true
}

resource "aws_sqs_queue" "process_strava_data_dql" {
  name = "proccess-strava-data-dlq"
}
