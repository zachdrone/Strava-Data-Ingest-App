resource "aws_cloudwatch_event_rule" "sqs_trigger_rule" {
  name        = "gpx-sqs-trigger-rule"
  description = "Trigger Step Function from SQS message"
  
  event_pattern = jsonencode({
    source      = ["aws.sqs"],
    detail-type = ["AWS API Call via CloudTrail"],
    detail = {
      eventSource = ["sqs.amazonaws.com"],
      requestParameters = {
        queueUrl = [aws_sqs_queue.strava_activity_queue.url]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "sfn_target" {
  rule      = aws_cloudwatch_event_rule.sqs_trigger_rule.name
  arn       = aws_sfn_state_machine.process_strava_data.arn
  role_arn  = aws_iam_role.eventbridge_sfn_role.arn
}

