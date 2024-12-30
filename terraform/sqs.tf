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

resource "aws_sqs_queue_policy" "sqs_policy" {
  queue_url = aws_sqs_queue.strava_activity_queue.url

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "events.amazonaws.com"
      },
      Action   = "SQS:SendMessage",
      Resource = aws_sqs_queue.strava_activity_queue.arn
    }]
  })
}

resource "aws_sqs_queue" "process_strava_data_trigger_dql" {
  name = "process_strava_data_trigger_dlq"
}

resource "aws_sqs_queue" "prepare_and_upload_gpx_dlq" {
  name = "prepare-and-upload-gpx-dlq"
}
