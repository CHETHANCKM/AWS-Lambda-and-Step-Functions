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
                    def FILE_NAME = "${env.APPLICATION_NAME}_${env.FUNCTION_NAME}_${env.ENVIRONMENT}".toLowerCase()
                    echo "Processing function: $FILE_NAME"  # Debug output

                    HANDLER=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'Handler:' | awk '{print $2}')
                    MEMORY=$(grep -A 5 " $FUNCTION_NAME:" template.yaml | grep 'MemorySize:' | awk '{print $2}')
                    echo "Handler: $HANDLER, Memory: $MEMORY, Timeout: $TIMEOUT, Runtime: $RUNTIME"


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
