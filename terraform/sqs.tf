resource "aws_sqs_queue" "strava_activity_queue" {
  name = "strava-activity-queue"
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.strava_activity_queue.arn
  function_name    = aws_lambda_function.process_strava_data.arn
  enabled          = true
}