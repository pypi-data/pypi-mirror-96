# MSCI ESG
---
## What is it?
This is a simple package that uses Selenium to scrape content from the MSCI.com [ESG (Environment, Sustainability, Governance) Corporate Search Tool](https://www.msci.com/our-solutions/esg-investing/esg-ratings/esg-ratings-corporate-search-tool/issuer/tesla-inc/IID000000002594878). 

---
## Why was this created?
ESG ratings play an important role in stock market analysis, and previously, the only way of obtaining this data from MSCI was to open the Search Tool in a browser, search for a symbol, and click on one of the autosuggested results. This automates the collection of the important ESG rating data, both historical and current, and returns it in JSON format. 
This project was built as a supplemental tool for [StockScope](https://github.com/austinjhunt/stockscope), which is a Django web application in development for providing AI-driven Stock Market querying and alerting capabilities. 