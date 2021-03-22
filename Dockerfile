FROM transportchallenge/transport_challenge_2021:latest

ADD run.sh /
ADD run_baseline_agent.sh /
ADD run_submission.sh /
ADD agent.py /

WORKDIR /