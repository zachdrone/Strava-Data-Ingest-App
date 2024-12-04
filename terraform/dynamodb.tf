resource "aws_dynamodb_table" "users" {
  name         = "users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "N"
  }
}

#resource "aws_dynamodb_table" "activities" {
#name         = "users"
#billing_mode = "PAY_PER_REQUEST"
#hash_key     = "activity_id"

#attribute {
#name = "activity_id"
#type = "N"
#}

#attribute {
#name = "parent_activity_id"
#type = "N"
#}

#attribute {
#name = "user_id"
#type = "N"
#}

#
#global_secondary_index {
#name            = "ParentActivityIdIndex"
#hash_key        = "parent_activity_id"
#projection_type = "ALL"
#}
#}
