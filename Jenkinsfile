pipeline {
    agent any

    environment {
        PROJECT_NAME = "my-sam-app"
        S3_BUCKET = "myproject-acc-dev"
        ARTIFACT_ZIP = "deployment.zip"
        TEMPLATE_FILE = "template.yaml"

        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION = "us-east-1"
    }

    stages {
        stage('Build') {
            steps {
                script {
                    sh '''
                    echo "🗑️ Removing old ZIP file..."
                    rm -f $ARTIFACT_ZIP

                    echo "📦 Compressing Python files into ZIP..."
                    zip -r9 $ARTIFACT_ZIP . -i "*.py"
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh '''
                    echo "🚀 Uploading ZIP to S3 (overwriting existing file)..."
                    aws s3 cp $ARTIFACT_ZIP s3://$S3_BUCKET/ --acl private --storage-class STANDARD

                    echo "📦 Packaging SAM Template..."
                    aws cloudformation package \
                        --template-file $TEMPLATE_FILE \
                        --s3-bucket $S3_BUCKET \
                        --s3-prefix myfolder \
                        --output-template-file packaged.yaml \
                        --force-upload

                    echo "🚀 Deploying to AWS..."
                    aws cloudformation deploy \
                        --template-file packaged.yaml \
                        --stack-name $PROJECT_NAME \
                        --capabilities CAPABILITY_IAM
                    '''
                }
            }
        }

        stage('Post Build') {
            steps {
                script {
                    sh '''
                    echo "📝 Cleaning up old files..."
                    rm -f $ARTIFACT_ZIP packaged.yaml
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
