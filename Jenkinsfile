pipeline {
    agent any
    
    environment {
        PROJECT_NAME = "my-sam-app"
        S3_BUCKET = "myproject-acc-dev"
        ARTIFACT_ZIP = "deployment.zip"
        TEMPLATE_FILE = "template.yaml"

        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')  // Fetch from Jenkins credentials
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')  // Fetch from Jenkins credentials
        AWS_DEFAULT_REGION = "us-east-1"
    }

    stages {
        stage('Setup AWS Credentials') {
            steps {
                script {
                    sh '''
                    if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
                        echo "❌ AWS credentials not found! Please configure AWS credentials in Jenkins."
                        exit 1
                    fi
                    '''
                }
            }
        }

        stage('Compress Python Files') {
            steps {
                script {
                    sh '''
                    echo "📦 Compressing Python files into ZIP..."
                    zip -r9 $ARTIFACT_ZIP . -i "*.py"
                    '''
                }
            }
        }

        stage('Upload to S3') {
            steps {
                script {
                    sh '''
                    echo "🚀 Uploading ZIP to S3..."
                    aws s3 cp $ARTIFACT_ZIP s3://$S3_BUCKET/ || { echo "❌ Failed to upload ZIP to S3"; exit 1; }
                    '''
                }
            }
        }

        stage('Package SAM Template') {
            steps {
                script {
                    sh '''
                    echo "📦 Packaging SAM Template..."
                    aws cloudformation package \
                        --template-file $TEMPLATE_FILE \
                        --s3-bucket $S3_BUCKET \
			            --s3-prefix myfolder \
                        --output-template-file packaged.yaml || { echo "❌ Failed to package CloudFormation template"; exit 1; }
                    '''
                }
            }
        }

        stage('Deploy to AWS') {
            steps {
                script {
                    sh '''
                    echo "🚀 Deploying to AWS..."
                    aws cloudformation deploy \
                        --template-file packaged.yaml \
                        --stack-name $PROJECT_NAME \
                        --capabilities CAPABILITY_IAM || { echo "❌ Deployment failed!"; exit 1; }
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment completed successfully!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
