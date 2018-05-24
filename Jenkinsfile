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

    stage('Cleanup') {
      steps {
        echo '*** Performing cleanup ***'
        sh 'ls /dev/vmm | xargs vm poweroff || true'
        sh 'ixautomation --destroy-all-vm'
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
                        junit 'tests/results/*.xml'
                    }
                }
                stage('Middleware Tests') {
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
                        sh 'cp -R freenas/src ${WORKSPACE}'
                        sh 'ixautomation --run middlewared-tests --systype freenas'
                        junit 'src/middlewared/middlewared/pytest/results/*.xml'
                    }
                }
                stage('WebUI Tests') {
                    agent {
                        label "QA"
                    }
                    steps {
                        sh 'rm -rf freenas || true'
                        sh 'rm -rf webui || true'
                        sh 'rm -rf tests || true'
                        sh 'git clone --depth=1 git://10.20.21.137/webui'
                        sh 'mkdir tests || true'
                        sh 'cp -R webui/tests/ tests/'
                        echo '*** Grabbing artifact from FreeNAS - Master - Incremental ***'
                        copyArtifacts filter: '**/*.iso', fingerprintArtifacts: true, flatten: true, projectName: 'FreeNAS - Master - Incremental Build', selector: lastSuccessful(), target: 'tests/iso'
                        sh 'find ${WORKSPACE}/tests/iso | grep NOGRUB.iso | xargs -I {} rm {}'
                        sh 'ixautomation --run webui-tests --systype freenas'
                        junit 'tests/results/*.xml'
                    }
                }
            }
        }
    
  }
}
