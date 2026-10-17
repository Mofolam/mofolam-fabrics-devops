pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    // Polls the configured SCM for changes. This works when Jenkins is local
    // (for example, http://localhost:8082) and cannot receive GitHub webhooks.
    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        IMAGE_NAME = 'oreoluu/mofolam-fabrics-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(
                        returnStdout: true,
                        script: 'git rev-parse --short=12 HEAD'
                    ).trim()
                }
                echo "Checked out source revision ${env.IMAGE_TAG}"
            }
        }

        stage('Install Dependencies and Run Tests') {
            agent {
                docker {
                    image 'python:3.14-slim'
                    args '-u root:root'
                    reuseNode true
                }
            }
            steps {
                sh '''#!/bin/sh
                    set -eu
                    python --version
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                    python -m pip install pytest
                    python -m pytest -v --junitxml=test-results.xml
                '''
            }
        }

        stage('Security Scan - Gitleaks') {
            agent {
                docker {
                    image 'python:3.14-slim'
                    args '-u root:root'
                    reuseNode true
                }
            }
            steps {
                sh '''#!/bin/sh
                    set -eu
                    apt-get update
                    apt-get install -y --no-install-recommends curl ca-certificates tar
                    GITLEAKS_VERSION='8.30.0'
                    curl -fsSL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" -o /tmp/gitleaks.tar.gz
                    echo '79a3ab579b53f71efd634f3aaf7e04a0fa0cf206b7ed434638d1547a2470a66e  /tmp/gitleaks.tar.gz' | sha256sum -c -
                    tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks
                    gitleaks version
                    gitleaks detect --source=. --verbose
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''#!/bin/sh
                    set -eu
                    docker version
                    docker build --pull \
                      -t "$IMAGE_NAME:$IMAGE_TAG" \
                      -t "$IMAGE_NAME:latest" \
                      .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''#!/bin/sh
                        set +x
                        set -eu
                        trap 'docker logout >/dev/null 2>&1 || true' EXIT
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USERNAME" \
                          --password-stdin
                        docker push "$IMAGE_NAME:$IMAGE_TAG"
                        docker push "$IMAGE_NAME:latest"
                    '''
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results.xml'
            archiveArtifacts(
                artifacts: 'test-results.xml',
                allowEmptyArchive: true,
                fingerprint: true
            )
            echo 'Mofolam Fabrics CI pipeline finished.'
        }
        success {
            echo 'Tests and security scan passed; Docker image was built and pushed.'
        }
        failure {
            echo 'Pipeline failed. Review the stage logs and published test results.'
        }
    }
}
