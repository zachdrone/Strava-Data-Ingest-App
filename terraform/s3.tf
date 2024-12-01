resource "aws_s3_bucket" "strava_data_bucket" {
  bucket = "zach-app-strava-data-bucket"
}

resource "aws_s3_bucket" "athena_query_results_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-athena-query-results"
}
