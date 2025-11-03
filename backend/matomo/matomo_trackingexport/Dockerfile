FROM python:3
ADD matomo_trackingexport.py .
RUN pip install requests beautifulsoup4
CMD [ "python","-u","matomo_trackingexport.py"]
