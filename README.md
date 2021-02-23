# scrape_regsho

Scrapes daily short sale volumes of all Nasdaq and NYSE stocks from 3/1/2011 to the present.

Dependencies
```
pip install xone==0.1.6
pip install pandas==1.2.2
pip install pytz==2021.1
pip install requests==2.25.1
```

Run to write/update `regsho_data.csv`
```
python scrape_regsho.py
```
