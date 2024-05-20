FROM python:3.11

WORKDIR /snow-amazing

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/sfc-gh-ktyler/ysa_spc.git .

RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "🏆_Snow_Amazing_Home_Page.py", "--server.port=8501", “–server.address=0.0.0.0”]
