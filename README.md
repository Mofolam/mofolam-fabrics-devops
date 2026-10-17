# Mofolam Fabrics — CI/CD with Jenkins and Docker

A fabric inventory application used to practise CI/CD, automated testing, containerization, security scanning, credentials management, and build artifact retention. GitHub Actions remains available in `.github/workflows/ci.yml`; the `Jenkinsfile` implements the corresponding Jenkins pipeline.

## Jenkins pipeline stages

1. **Checkout** — checks out the repository configured in the Jenkins job and records the Git commit ID for image tagging.
2. **Install Dependencies and Run Tests** — uses a `python:3.14-slim` Docker agent, installs the project dependencies and `pytest`, runs the test suite, and writes `test-results.xml` in JUnit format.
3. **Security Scan — Gitleaks** — scans the checked-out source and Git history for accidentally committed secrets. A finding fails the pipeline and should be investigated before publishing an image. The scan runs in a Docker-based Python agent so it reads the Jenkins workspace directly; it downloads the pinned Gitleaks v8.30.0 release and verifies its SHA-256 checksum before running it.
4. **Build Docker Image** — builds `oreoluu/mofolam-fabrics-app` with both a commit-specific tag and `latest`.
5. **Push Docker Image** — logs in to Docker Hub through Jenkins Credentials Binding and pushes both tags. The token is not stored in this repository.
6. **Post-build publishing** — publishes the JUnit report and archives `test-results.xml` when the test runner creates it. The raw security scan output stays in the build log rather than being published as an artifact that could expose detected secret values.

## Jenkins requirements

Install or verify these plugins under **Manage Jenkins → Plugins**:

- Pipeline
- Pipeline: Declarative
- Git
- Credentials Binding
- Docker Pipeline
- JUnit (often already installed as a dependency)
- Timestamper (for timestamped console output)
- GitHub (optional, if you later configure GitHub webhooks)

The Jenkins agent/controller that runs this pipeline must have the Docker CLI installed and access to a working Docker daemon. The existing `Jenkinsfile` uses a Docker-based Python test agent and invokes Docker for the Gitleaks scan, image build, and push. Verify `docker version` in a Jenkins pipeline before troubleshooting the application code. In a containerized Jenkins setup, this normally requires the Docker CLI and appropriate access to the Docker socket/daemon; do not expose the Docker socket to untrusted jobs because it grants powerful host-level access.

## Configure Docker Hub credentials

1. In Jenkins, open **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**.
2. Choose **Username with password**.
3. Username: your Docker Hub username (`oreoluu`).
4. Password: a Docker Hub access token with permission to push images to `oreoluu/mofolam-fabrics-app`.
5. Set **ID** to exactly `dockerhub-creds` and save.

Do not put the token in the `Jenkinsfile`, `.env`, `README.md`, or Git history. If a token was committed or exposed, revoke it and create a new one.

## Configure the Jenkins job

1. Open Jenkins at `http://localhost:8082` for the current local setup.
2. Select **New Item**, enter a job name such as `Mofolam Fabrics CI`, and choose **Pipeline**.
3. Under **Pipeline**, select **Pipeline script from SCM**.
4. SCM: **Git**. Repository URL: `https://github.com/Mofolam/mofolam-fabrics-devops.git`.
5. Branch specifier: `*/main`.
6. Script path: `Jenkinsfile`.
7. Save and select **Build Now** for the first run.

The pipeline declares `pollSCM('H/5 * * * *')`, which asks Jenkins to check the configured repository for changes approximately every five minutes. Jenkins must have SCM polling enabled for the job. This is suitable for a Jenkins instance reachable only through `localhost`; GitHub cannot send a webhook directly to your local machine. To use a webhook later, Jenkins must be reachable from GitHub over a properly secured public URL or tunnel, and the relevant GitHub integration must be configured.

## Verify a successful build

A successful build should show these stages as successful:

- Checkout
- Install Dependencies and Run Tests
- Security Scan — Gitleaks
- Build Docker Image
- Push Docker Image

Open the build's **Test Result** page to review tests. Open **Artifacts** to download archived result files. Confirm the Docker Hub repository contains both `latest` and the commit-specific image tag.

If the push fails with an authentication or scope error, verify the Jenkins credential ID and replace the Docker Hub token with one that has the required write permission. If the build fails at `docker version`, fix Docker CLI/daemon access in Jenkins before changing the application pipeline.

## Local application

The local development application can continue running with Docker Compose. The Jenkins image publishing stages do not replace or automatically redeploy the currently running local application; deployment is a separate stage and should be configured deliberately after CI and registry publishing pass.
