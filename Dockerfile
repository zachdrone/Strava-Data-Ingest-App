FROM public.ecr.aws/lambda/python:3.13

RUN pip install --no-cache-dir poetry

ENV PATH="/root/.local/bin:$PATH"

ENV PYTHONPATH="/var/task"

WORKDIR /var/task

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install

COPY . .

RUN python -c "import aws_lambda_powertools"

CMD ["lambda_handler.lambda_handler"]
# ENTRYPOINT ["/bin/bash"]