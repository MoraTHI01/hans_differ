FROM python:3
ADD matomo_init.py .
RUN pip install requests beautifulsoup4 pythonping
CMD [ "python","-u","matomo_init.py"]
