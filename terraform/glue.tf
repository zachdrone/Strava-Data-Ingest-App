resource "aws_glue_catalog_database" "strava_catalog_db" {
  name = "strava_catalog_db"
}

resource "aws_glue_crawler" "strava_data_crawler" {
  database_name = aws_glue_catalog_database.strava_catalog_db.name
  name          = "strava_catalog_db"
  role          = aws_iam_role.glue_execution_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.strava_parquet_data_bucket.bucket}"
  }
}
