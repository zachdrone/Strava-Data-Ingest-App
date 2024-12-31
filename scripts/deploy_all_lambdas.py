import boto3
import re


def main():
    lambda_client = boto3.client("lambda")

    def replace_tag_with_latest(image_uri: str) -> str:
        """
        Given an ECR image URI like:
          123456789012.dkr.ecr.us-east-1.amazonaws.com/my-image:some-tag
        return the same URI with the tag replaced by :latest
        """
        # Remove everything after the last colon and replace it with :latest
        return re.sub(r":[^/]+$", ":latest", image_uri)

    paginator = lambda_client.get_paginator("list_functions")

    for page in paginator.paginate():
        for fn in page["Functions"]:
            # Only proceed if the Lambda PackageType is 'Image'
            if fn.get("PackageType") == "Image":
                function_name = fn["FunctionName"]

                # Retrieve detailed info about the function to get the actual image URI
                func_details = lambda_client.get_function(FunctionName=function_name)
                code_info = func_details.get("Code", {})

                image_uri = code_info.get("ImageUri")
                if image_uri:
                    new_image_uri = replace_tag_with_latest(image_uri)
                    print(
                        f"Updating {function_name} from {image_uri} to {new_image_uri}..."
                    )
                    lambda_client.update_function_code(
                        FunctionName=function_name, ImageUri=new_image_uri
                    )


if __name__ == "__main__":
    main()
