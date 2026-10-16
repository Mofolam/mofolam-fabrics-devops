
pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root:root'
        }
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python --version'
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
                sh 'pip install pytest'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest -v'
            }
        }

        stage('Build Docker Image') {
            agent {
                docker {
                    image 'jenkins-with-docker-cli:latest'
                    args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                sh 'docker version'
                sh 'docker build -t mofolam-fabrics-app:ci .'
            }
        }
    }

    post {
        always {
            echo 'Mofolam Fabrics CI pipeline finished.'
        }
    }
}
