resource "aws_sfn_state_machine" "process_strava_data" {
  name     = "process-strava-data"
  role_arn = aws_iam_role.step_function_role.arn

  definition = templatefile("${path.module}/process_strava_data_sfn.json.tpl", {
    Region    = var.aws_region,
    AccountId = data.aws_caller_identity.current.account_id
  })
}
