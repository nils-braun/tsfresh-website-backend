FROM continuumio/miniconda

COPY ./requirements.txt .
RUN conda install -y --quiet \
        --file requirements.txt -c conda-forge \
 && conda clean -y -f

COPY ./backend /app/

ENV PORT 8080
ENV HOST 0.0.0.0

EXPOSE 8080
CMD uvicorn app.main:app --host $HOST --port $PORT
