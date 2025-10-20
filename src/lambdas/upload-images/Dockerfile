FROM public.ecr.aws/lambda/python:3.11

# working directory
WORKDIR /var/task

# dependencies
#COPY requirements.txt .
#RUN pip install -r requirements.txt

# handler file
COPY app.py .

# {filename}.py > function name in {filename}.py
CMD ["app.handler"]