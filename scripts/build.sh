aws ecr --profile strava get-login-password --region us-east-1 | docker login --username AWS --password-stdin 302263086197.dkr.ecr.us-east-1.amazonaws.com
docker build --provenance=false --platform linux/amd64 -t my-lambda-repo .
docker tag my-lambda-repo:latest 302263086197.dkr.ecr.us-east-1.amazonaws.com/my-lambda-repo:latest
docker push 302263086197.dkr.ecr.us-east-1.amazonaws.com/my-lambda-repo:latest