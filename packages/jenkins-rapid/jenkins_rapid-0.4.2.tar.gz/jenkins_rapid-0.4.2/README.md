
# Jenkins Rapid 

A commandline tool to quickly develop/debug Jenkins piepline using jenkins files



## Install 

        $ pip install jenkins-rapid

## Usage: 

        # Create/Upated pipeline and tiggers build
            $ jrp --job <job_name> --url <jenkins_url> --user <username> --token <user_api_tokern>
        # Deletes job
            $ jrp delete --job <job_name> --url <jenkins_url> --user <username> --token <user_api_tokern>


## Features

- Upload jenkinsfile from local
- Create jobs with parameters
- Triggers jenkins jobs
- Streams log output to terminal
- Stop jobs running jobs from terminal
- Delete jenkins jobs
- Work with Jenkinsfiles directly from your favorite IDE



## Additonal info 

- Environment variables can be set for the following values for jenkins url and user credentials and will take presedence over commandline arguments 

        #	JENKINS_URL
        #	JENKINS_USER
        #	JENKINS_PASSWORD
		#
		Ex:
		export JENKINS_URL=http://localhost:8080
		export JENKINS_USER=admin
        export JENKINS_PASSWORD=<jenkins_api_token>
