# Products-scrapper
> Fields: Data scraping, data analysis and Machine learning

> Technologies: Scrapy, Spacy, Python

## Content
1. [Description of the project](#description-of-the-project)
2. [User requirements](#user-requirements)
3. [Accomplishments](#accomplishments)
4. [How to use the project](#how-to-use-the-project)
5. [Understanding the code](#understanding-the-code)
6. [How to use the project](#how-to-use-the-project)

### Description of the project
A project I received as a test from an employer for the recruitment process, for a machine learning and data analysis company. The project has been very well received by my employer, thus securing me the job for which I have applied. 

### User requirements
- Build a spider that crawls a list of websites that contain products.
- Extract valuable text from these websites, regarding information about the products.
- Tag the products found on these websites, with the entity "PRODUCT".
- Build a Spacy model that will recognize products on different websites.

### Accomplishments
- Build a spider with Scrapy, that will gather data from the list of websites.
- Preprocess the data in order to eliminate useless or redundant information.
- Use the information given by the URLs regarding the product in order to identify the name of the product.
- Use a dictionary in order to check that the product contains at least one word related to products.
- Split the data in two categories, for ease of access: sentences with entities, sentences without entities.
- Build a custom spacy model for NER (Named Entity Recognition) that will be trained to detect a new NER, namely "PRODUCT".
- F1-score, precision and recall are approximately 92%.
- Build a custom library for several processes that can be used again in future iterations or projects.
- Design a modular code that can be easily upgraded and a pipeline of functions that fullfil precise tasks.


