#based on https://blog.knoldus.com/running-a-cron-job-in-docker-container/
FROM ubuntu:20.04
LABEL anoderay

# Install cron, Python3 and pip
RUN apt-get update && apt-get install -y cron && apt-get install python3 -y && apt-get install python3-pip -y

#install python dependency
RUN python3 -m pip install imap_tools

# Add files
ADD run.sh /run.sh
ADD entrypoint.sh /entrypoint.sh
ADD main.py /main.py

RUN mkdir log
RUN mkdir output
 
RUN chmod +x /run.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh
