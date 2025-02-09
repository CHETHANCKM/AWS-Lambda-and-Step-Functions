pipeline {
    agent any
    environment {
        APPLICATION_NAME = "data-movement"
        ENVIRONMENT = "${env.GIT_BRANCH}"
        S3_BUCKET = 'myproject-acc-dev'
        ROLE_ARN = 'arn:aws:iam::437563065463:role/LAMBDA_FULLACCESS_ROLE_DEV'  // Update this
        DEFAULT_RUNTIME = 'python3.9'  // Default runtime
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION = "us-east-1"

    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Parse YAML and Deploy') {
            steps {
                sh '''
                echo "🗑️ Cleaning old ZIP files..."
                rm -f *.zip

                # Extract function names (assuming they are under "Resources" in template.yaml)
                FUNCTIONS=$(grep -E '^[[:space:]]{2}[A-Za-z0-9_-]+:' template.yaml | awk '{print $1}' | tr -d ':' | tr '\n' ' ')


                for FUNCTION_NAME in $FUNCTIONS; do
                    FILE_NAME = "${APPLICATION_NAME}_${FUNCTION_NAME}_${ENVIRONMENT}"
                    echo "Processing function: $FUNCTION_NAME"  # Debug output

                    HANDLER=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'Handler:' | awk '{print $2}')
                    MEMORY=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'MemorySize:' | awk '{print $2}')
                    echo "Handler: $HANDLER, Memory: $MEMORY, Timeout: $TIMEOUT, Runtime: $RUNTIME"

                    ZIP_FILE="${FILE_NAME}.zip"
                    
                    echo "📦 Creating ZIP for $FILE_NAME..."
                    zip -r9 "$ZIP_FILE" "$FILE_NAME.py"

                    echo "🚀 Uploading $ZIP_FILE to S3..."
                    aws s3 cp "$ZIP_FILE" "s3://$S3_BUCKET/$ZIP_FILE"

                    echo "🛠️ Creating/Updating Lambda Function: $FILE_NAME..."

                    aws lambda create-function \
                        --function-name "$FILE_NAME" \
                        --runtime "$DEFAULT_RUNTIME" \
                        --role "$ROLE_ARN" \
                        --handler "$HANDLER" \
                        --code "S3Bucket=$S3_BUCKET,S3Key=$ZIP_FILE" \
                        --timeout 900 \
                        --memory-size $MEMORY || \
                        
                    aws lambda update-function-code \
                        --function-name "$FILE_NAME" \
                        --s3-bucket "$S3_BUCKET" \
                        --s3-key "$ZIP_FILE"
                done
                '''
            }
        }
    }
    post {
        success {
            echo '✅ Lambda functions deployed successfully!'
        }
        failure {
            echo '❌ Deployment failed!'
        }
    }
}
