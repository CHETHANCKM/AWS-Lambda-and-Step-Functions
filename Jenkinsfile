pipeline {
    agent any
    environment {
        S3_BUCKET = 'myproject-acc-dev'
        ROLE_ARN = 'arn:aws:iam::123456789012:role/my-lambda-role'  // Update this
        DEFAULT_RUNTIME = 'python3.8'  // Default runtime
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')

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
                FUNCTIONS=$(grep -E '^[[:space:]]{2}[A-Za-z0-9_-]+:' template.yaml | awk '{print $1}' | tr -d ':')

                for FUNCTION_NAME in $FUNCTIONS; do
                    HANDLER=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'Handler:' | awk '{print $2}')
                    MEMORY=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'MemorySize:' | awk '{print $2}')
                    TIMEOUT=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'Timeout:' | awk '{print $2}')
                    RUNTIME=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'Runtime:' | awk '{print $2}')

                    # Fallback to default values if not found
                    [ -z "$MEMORY" ] && MEMORY=128
                    [ -z "$TIMEOUT" ] && TIMEOUT=30
                    [ -z "$RUNTIME" ] && RUNTIME=$DEFAULT_RUNTIME

                    ZIP_FILE="${FUNCTION_NAME}.zip"
                    
                    echo "📦 Creating ZIP for $FUNCTION_NAME..."
                    zip -r9 "$ZIP_FILE" "$FUNCTION_NAME.py"

                    echo "🚀 Uploading $ZIP_FILE to S3..."
                    aws s3 cp "$ZIP_FILE" "s3://$S3_BUCKET/$ZIP_FILE"

                    echo "🛠️ Creating/Updating Lambda Function: $FUNCTION_NAME..."
                    aws lambda create-function \
                        --function-name "$FUNCTION_NAME" \
                        --runtime "$RUNTIME" \
                        --role "$ROLE_ARN" \
                        --handler "$HANDLER" \
                        --code "S3Bucket=$S3_BUCKET,S3Key=$ZIP_FILE" \
                        --timeout $TIMEOUT \
                        --memory-size $MEMORY || \
                    aws lambda update-function-code \
                        --function-name "$FUNCTION_NAME" \
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
