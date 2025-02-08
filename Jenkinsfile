pipeline {
    agent any
    environment {
        S3_BUCKET = 'myproject-acc-dev'
        ROLE_ARN = 'arn:aws:iam::437563065463:role/LAMBDA_FULLACCESS_ROLE_DEV'  // Update this
        RUNTIME = 'python3.8'  // Default runtime, will be overridden if present in YAML
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Parse YAML and Build') {
            steps {
                sh '''
                echo "🗑️ Cleaning old ZIP files..."
                rm -f *.zip

                # Extract Lambda function names from template.yaml
                FUNCTIONS=$(yq e '.Resources | keys | .[]' template.yaml)

                for FUNCTION_NAME in $FUNCTIONS; do
                    HANDLER=$(yq e ".Resources.$FUNCTION_NAME.Properties.Handler" template.yaml)
                    MEMORY=$(yq e ".Resources.$FUNCTION_NAME.Properties.MemorySize" template.yaml)
                    TIMEOUT=$(yq e ".Resources.$FUNCTION_NAME.Properties.Timeout" template.yaml)
                    RUNTIME=$(yq e ".Resources.$FUNCTION_NAME.Properties.Runtime" template.yaml)
                    
                    [ "$MEMORY" = "null" ] && MEMORY=128
                    [ "$TIMEOUT" = "null" ] && TIMEOUT=30
                    [ "$RUNTIME" = "null" ] && RUNTIME=$RUNTIME

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
