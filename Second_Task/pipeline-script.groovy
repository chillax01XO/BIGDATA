pipeline {
    agent any

    environment {
        VENV_PATH = '/workspace/.venv'
    }

    triggers {
        cron('H 2 * * *') // запуск каждый день в 2:00
    }

    stages {
        stage('Setup venv & Install requirements') {
            steps {
                sh '''
                    python3 -m venv $VENV_PATH
                    . $VENV_PATH/bin/activate
                    pip install --upgrade pip
                    pip install psycopg2-binary pandas
                '''
            }
        }
        stage('Run ETL') {
            steps {
                sh '''
                    . $VENV_PATH/bin/activate
                    python /workspace/etl.py
                '''
            }
        }
    }
}
