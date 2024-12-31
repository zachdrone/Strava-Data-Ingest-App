{
  "StartAt": "store_activity_in_dynamo",
  "States": {
    "store_activity_in_dynamo": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:store_activity_in_dynamo",
      "Parameters": {
        "activity_id.$": "$.activity_id",
        "user_id.$": "$.user_id"
      },
      "ResultPath": "$.store_activity_in_dynamo",
      "Next": "prepare_and_upload_gpx"
    },
    "prepare_and_upload_gpx": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:prepare_and_upload_gpx",
      "ResultPath": "$.prepare_and_upload_gpx",
      "Next": "prepare_and_upload_parquet"
    },
    "prepare_and_upload_parquet": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:prepare_and_upload_parquet",
      "ResultPath": "$.prepare_and_upload_parquet",
      "Next": "check_child_users"
    },
    "check_child_users": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:check_child_users",
      "Parameters": {
        "user_id.$": "$.user_id"
      },
      "ResultPath": "$.check_child_users",
      "Next": "validate_for_each_child"
    },
    "validate_for_each_child": {
      "Type": "Map",
      "ItemsPath": "$.check_child_users.child_users",
      "ItemSelector": {
        "child_id.$": "$$.Map.Item.Value.child_id",
        "parent_id.$": "$.user_id",
        "activity_id.$": "$.activity_id",
        "activity_name.$": "$.prepare_and_upload_gpx.activity_name",
        "activity_sport_type.$": "$.prepare_and_upload_gpx.activity_sport_type",
        "gpx_data_s3_key.$": "$.prepare_and_upload_gpx.gpx_data_s3_key"
      },
      "Iterator": {
        "StartAt": "validate_child",
        "States": {
          "validate_child": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:validate_child",
            "Parameters": {
              "activity_name.$": "$.activity_name",
              "child_id.$": "$.child_id",
              "parent_id.$": "$.parent_id"
            },
            "ResultPath": "$.validate_child",
            "Next": "validation_choice"
          },
          "validation_choice": {
            "Type": "Choice",
            "Choices": [
              {
                "And": [
                  {
                    "Variable": "$.validate_child.parent_valid",
                    "BooleanEquals": true
                  },
                  {
                    "Variable": "$.validate_child.title_valid",
                    "BooleanEquals": true
                  }
                ],
                "Next": "duplicate_activity"
              }
            ],
            "Default": "skip_child"
          },
          "duplicate_activity": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:duplicate_activity",
            "Parameters": {
              "gpx_data_s3_key.$": "$.gpx_data_s3_key",
              "activity_sport_type.$": "$.activity_sport_type",
              "child_id.$": "$.child_id"
            },
            "ResultPath": "$.duplicate_activity",
            "Next": "initialize_retry_counter"
          },
          "initialize_retry_counter": {
            "Type": "Pass",
            "Result": {
              "retry_count": 0
            },
            "ResultPath": "$.retry",
            "Next": "wait_for_duplication"
          },
          "wait_for_duplication": {
            "Type": "Wait",
            "Seconds": 30,
            "Next": "check_duplication_status"
          },
          "check_duplication_status": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:check_duplication_status",
            "Parameters": {
              "child_id.$": "$.child_id",
              "upload_id.$": "$.duplicate_activity.upload_id"
            },
            "ResultPath": "$.check_duplication_status",
            "Next": "duplication_complete_choice"
          },
          "duplication_complete_choice": {
            "Type": "Choice",
            "Choices": [
              {
                "And": [
                  {
                    "Variable": "$.check_duplication_status.child_activity_id",
                    "IsNull": false
                  },
                  {
                    "Variable": "$.check_duplication_status.error",
                    "IsNull": true
                  }
                ],
                "Next": "store_child_activity_in_dynamo"
              },
              {
                "Variable": "$.check_duplication_status.error",
                "IsNull": false,
                "Next": "duplication_upload_failed"
              }
            ],
            "Default": "check_max_retries"
          },
          "check_max_retries": {
            "Type": "Choice",
            "Choices": [
              {
                "Variable": "$.retry.retry_count",
                "NumericGreaterThanEquals": 10,
                "Next": "duplication_timed_out"
              }
            ],
            "Default": "increment_retry_counter"
          },
          "increment_retry_counter": {
            "Type": "Pass",
            "Parameters": {
              "retry_count.$": "States.MathAdd($.retry.retry_count, 1)"
            },
            "ResultPath": "$.retry",
            "Next": "wait_for_duplication"
          },
          "duplication_timed_out": {
            "Type": "Fail",
            "Cause": "Duplication Timed Out",
            "Error": "Duplication did not complete after 10 attempts"
          },
          "duplication_upload_failed": {
            "Type": "Fail",
            "Cause": "Duplication upload failed",
            "Error": "Activity failed to upload"
          },
          "store_child_activity_in_dynamo": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:store_activity_in_dynamo",
            "Parameters": {
              "user_id.$": "$.child_id",
              "activity_id.$": "$.check_duplication_status.child_activity_id",
              "parent_id.$": "$.parent_id",
              "parent_activity_id.$": "$.activity_id"
            },
            "ResultPath": "$.store_child_activity_in_dynamo",
            "End": true
          },
          "skip_child": {
            "Type": "Succeed"
          }
        }
      },
      "ResultPath": "$.processed_child_users",
      "End": true
    }
  }
}
