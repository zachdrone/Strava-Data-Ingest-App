resource "aws_s3_bucket" "strava_parquet_data_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-strava-parquet-data"
}

resource "aws_s3_bucket" "strava_gpx_data_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-strava-gpx-data"
}

resource "aws_s3_bucket" "athena_query_results_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-athena-query-results"
}

resource "aws_s3_bucket" "zach_app_terraform_state_bucket" {
  bucket = "zach-app-terraform-state-bucket"
}
