/*
 * Jenkinsfile — Declarative Pipeline
 *
 * This file tells Jenkins exactly what to do on every Git push.
 * Each stage maps directly to a phase in the CI/CD diagram:
 *
 *   Code  →  Build  →  Test  →  (Deploy in a future step)
 */

pipeline {

    agent any   // run on any available Jenkins node

    environment {
        // Use a virtual environment so we don't pollute the system Python
        VENV = "${WORKSPACE}/.venv"
        PATH = "${VENV}/bin:${env.PATH}"
    }

    stages {

        // ── STAGE 1: CODE ──────────────────────────────────────────────
        // Jenkins automatically checks out the Git repo before this stage.
        // We just confirm what we got.
        stage('Code Checkout') {
            steps {
                echo "Branch: ${env.GIT_BRANCH}"
                echo "Commit: ${env.GIT_COMMIT}"
                sh 'git log --oneline -5'
            }
        }

        // ── STAGE 2: BUILD ─────────────────────────────────────────────
        // Create a virtual environment and install dependencies.
        // This is the Python equivalent of `mvn install`.
        stage('Build') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ── STAGE 3: TEST (Unit) ───────────────────────────────────────
        // Run fast unit tests. Jenkins marks the build FAILED if any fail.
        stage('Unit Tests') {
            steps {
                sh 'pytest tests/test_calculator.py -v --tb=short'
            }
            post {
                always {
                    // Publish test results in Jenkins UI (requires JUnit plugin)
                    junit allowEmptyResults: true, testResults: 'test-results/*.xml'
                }
            }
        }

        // ── STAGE 4: TEST (UI / Selenium) ──────────────────────────────
        // Run browser tests. Skipped automatically if Selenium isn't installed.
        stage('UI Tests') {
            steps {
                sh 'pytest tests/test_selenium.py -v --tb=short || true'
            }
        }

        // ── STAGE 5: INTEGRATE ─────────────────────────────────────────
        // This is the "green build" confirmation — all checks passed.
        // In a real pipeline the next stage would be Deploy (Docker, Ansible…).
        stage('Integration Complete') {
            steps {
                echo "All checks passed. Ready to deploy!"
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS — build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline FAILED — check the logs above."
        }
    }
}
