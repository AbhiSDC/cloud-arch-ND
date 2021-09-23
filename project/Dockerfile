FROM python:2.7
LABEL maintainer="Demo"

# COPY ./techtrends /techtrends
COPY project/techtrends /techtrends
WORKDIR /techtrends
RUN pip install -r requirements.txt

EXPOSE 3111
# command to run on container start
CMD [ "python", "app.py" ]
