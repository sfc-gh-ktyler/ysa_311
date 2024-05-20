WORKDIR /snow-amazing

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/sfc-gh-ktyler/ysa.git .

RUN pip3 install streamlit
RUN pip3 install boto3
RUN pip3 install snowflake-connector-python

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "🏆_Snow_Amazing_Home_Page.py", "--server.port=8501"
