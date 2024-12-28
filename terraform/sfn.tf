resource "aws_sfn_state_machine" "process_strava_data" {
  name     = "process-strava-data"
  role_arn = aws_iam_role.step_function_role.arn

  definition = file("${path.module}/process_strava_data_sfn.asl.json")
}
