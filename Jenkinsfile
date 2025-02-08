pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
		samDeploy([credentialsId: 'jenkins', kmsKeyId: '', outputTemplateFile: '', region: 'us-east-1', roleArn: '', s3Bucket: 'myproject-acc-dev', s3Prefix: '', stackName: 'test-stack1', templateFile: 'template.yaml'])
            }
        }
    }
}