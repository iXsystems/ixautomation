pipeline {
  agent {
    label 'QA'
  }

  stages {

    stage('Checkout') {
      steps {
        echo '*** Checking out test repositories ***'
        sh 'rm -rf freenas || true'
        sh 'rm -rf webui || true'
        sh 'rm -rf tests || true'
      }
    }

 stage('Run Tests') {
            parallel {
                stage('API 1.0') {
                    agent {
                        label "QA"
                    }
                    steps {
                        sh 'rm -rf freenas || true'
                        sh 'rm -rf webui || true'
                        sh 'rm -rf tests || true'
                        sh 'git clone --depth=1 git://10.20.21.137/freenas'
                        sh 'mkdir tests || true'
                        sh 'cp -R freenas/tests/ tests/'
                        echo '*** Grabbing artifact from FreeNAS - Master - Incremental ***'
                        copyArtifacts filter: '**/*.iso', fingerprintArtifacts: true, flatten: true, projectName: 'FreeNAS - Master - Incremental Build', selector: lastSuccessful(), target: 'tests/iso'
                        sh 'find ${WORKSPACE}/tests/iso | grep NOGRUB.iso | xargs -I {} rm {}'
                        sh 'ixautomation --run api-tests --systype freenas'
                        archiveArtifacts artifacts: 'tests/artifacts/*', fingerprint: true
                        junit 'tests/results/*.xml'
                    }
                }
                stage('API 2.0') {
                    agent {
                        label "QA"
                    }
                    steps {
                        sh 'rm -rf freenas || true'
                        sh 'rm -rf webui || true'
                        sh 'rm -rf tests || true'
                        sh 'git clone --depth=1 git://10.20.21.137/freenas'
                        sh 'mkdir tests || true'
                        sh 'cp -R freenas/tests/ tests/'
                        echo '*** Grabbing artifact from FreeNAS - Master - Incremental ***'
                        copyArtifacts filter: '**/*.iso', fingerprintArtifacts: true, flatten: true, projectName: 'FreeNAS - Master - Incremental Build', selector: lastSuccessful(), target: 'tests/iso'
                        sh 'find ${WORKSPACE}/tests/iso | grep NOGRUB.iso | xargs -I {} rm {}'
                        sh 'ixautomation --run api2-tests --systype freenas'
                        archiveArtifacts artifacts: 'tests/artifacts/*', fingerprint: true
                        junit 'tests/results/*.xml'
                    }
                    post {
                        always {
                            script {
                                cleanWs notFailBuild: true
                                    dir("${env.WORKSPACE}") {
                                        deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@tmp") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@2") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@2@tmp") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@3") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@3@tmp") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@4") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@4@tmp") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@5") {
                                            deleteDir()
                                    }
                                    dir("${env.WORKSPACE}@5@tmp") {
                                            deleteDir()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
}
