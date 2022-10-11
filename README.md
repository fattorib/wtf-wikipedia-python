# 

Python script for creating [LM_Dataformat](https://github.com/leogao2/lm_dataformat) from a Mongo created with [wtf_wikipedia](https://github.com/spencermountain/wtf_wikipedia) and [dumpster-dive](https://github.com/spencermountain/dumpster-dive)


## Instructions

(Steps 0 and 1 copied from [dumpster-dive](https://github.com/spencermountain/dumpster-dive))

0. Install [nodejs](https://nodejs.org/en/) (at least `v6`), [mongodb](https://docs.mongodb.com/manual/installation/) (at least `v3`)

1. Install ```dumpster-dive```:
```bash 
# install this script
npm install -g dumpster-dive # (that gives you the global command `dumpster`)
# start mongo up
mongod --config /mypath/to/mongod.conf
```

2. Install Python requirements:
```bash 
pip install -r requirements
```

3. Download and extract your copy of Wikitext. Make sure you have plenty of extra space when you do this. For the 20221006 dump, the uncompressed XML file is ~91GB! 

4. Extract XML to Mongo:

For our extract, we skip the following sections as they usually contain little-to-no actual text content:
- infoboxes
- redirects
- disambiguations
- citations
- links

```bash 
dumpster ./enwiki-latest-pages-articles.xml --plaintext=true --infoboxes=false --citations=false --categories=false --links=false
```

On a modern desktop CPU this process takes around 90 minutes. 

4. Stream data from Mongo to LM_Dataformat:

```bash
python stream_db.py
```

This process takes around 25 minutes. 

## Content Filtration Used

Quick Summary of content filtration used:

Wherever possible, we follow the methodology of [Wiki-40B: Multilingual Language Model Dataset](https://aclanthology.org/2020.lrec-1.297/) by Guo et al. when filtering the extracted text:

- Sections like 'References', 'See Also', and 'Further Reading' are excluded.
- Lists, Links, Images, Captions and Tables are excluded.
- Disambiguation Pages and Redirect Pages are excluded.
- As a proxy for removing Non-entity sections, we skip all articles that start with 'List of'. The majority of these articles are lists providing almost no text content (ex: [this](https://en.wikipedia.org/wiki/List_of_decades,_centuries,_and_millennia) and [this](https://en.wikipedia.org/wiki/List_of_cities_and_municipalities_in_the_Philippines))
- At the article level, we perform minimal formatting. Sections and paragraphs are joined together with ```\n\n``` and sections containing little (5 or fewer words) to no text content are skipped. 



## Pile V2 Stats:

- Wikipedia Dump Date: 2022-10-06
- Number of Included Articles: 6098081
- Archive Size (Jsonlines): 15.8GB