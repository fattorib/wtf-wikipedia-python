# 

Python script for creating [LM_Dataformat](https://github.com/leogao2/lm_dataformat) from a Mongo created with [wtf_wikipedia](https://github.com/spencermountain/wtf_wikipedia) and [dumpster-dive](https://github.com/spencermountain/dumpster-dive)


## Instructions

(Steps 0 and 1 copied from [dumpster-dive](https://github.com/spencermountain/dumpster-dive))

0. Install [nodejs](https://nodejs.org/en/) (at least `v6`), [mongodb](https://docs.mongodb.com/manual/installation/) (at least `v3`)

1. **Install ```dumpster-dive```**:
```bash 
# install this script
npm install -g dumpster-dive # (that gives you the global command `dumpster`)
# start mongo up
mongod --config /mypath/to/mongod.conf
```

2. **Install Python requirements**:
```bash 
pip install -r requirements
```

3. **Download and extract your copy of Wikitext.** Make sure you have plenty of extra space when you do this. For the 20221006 dump, the uncompressed XML file is ~91GB! 

4. **Load the XML to Mongo:** 
```bash 
dumpster ./enwiki-latest-pages-articles.xml --plaintext=true --infoboxes=false --citations=false --categories=false --links=false
```

For our extract, we skip the following sections as they usually contain little-to-no actual text content:
- infoboxes
- redirects
- disambiguations
- citations
- links

On a modern desktop CPU this process takes around 90 minutes. 

4. **Stream data from Mongo to LM_Dataformat**:

```bash
python stream_db.py
```

This process takes around 25 minutes. 

## Content Filtration Used

Quick Summary of content filtration used:

Wherever possible, article filtering follows the methodology of [Wiki-40B: Multilingual Language Model Dataset](https://aclanthology.org/2020.lrec-1.297/) by Guo et al:

- Sections like 'References', 'See Also', and 'Further Reading' are excluded from the dataset.
- Lists, Links, Images, Captions and Tables are excluded from the dataset.
- Disambiguation Pages and Redirect Pages are excluded from the dataset.

There is also some additional filtration to filter out content that ```wtf_wikipedia``` doesnt filter for:
- As a proxy for removing Non-entity sections in Guo et al, the majority of articles with titles starting with 'List of' are skipped. Most of these articles are lists providing almost no text content (ex: [this](https://en.wikipedia.org/wiki/List_of_decades,_centuries,_and_millennia) and [this](https://en.wikipedia.org/wiki/List_of_cities_and_municipalities_in_the_Philippines)). To catch cases where an article starts with 'List of' but still contains a significant of high-quality text (ex: [this](https://en.wikipedia.org/wiki/List_of_James_Bond_films) and [this](https://en.wikipedia.org/wiki/List_of_Marvel_Cinematic_Universe_films)), all 'List of' titles are filtered against Wikipedia's List of [Featured Lists](https://en.wikipedia.org/wiki/Wikipedia:Featured_lists) as these articles contain more content than just the list values themselves. See [here](https://en.wikipedia.org/wiki/Wikipedia:Featured_list_criteria) for the full criteria of a Featured List. 

-  Sections containing 5 or fewer words to no text content are skipped as these sections are usually lists with some text preamble. 

- At the article level, formatting follows PileV1 Wikipedia. Titles, sections and paragraphs are joined together with ```\n\n```. 



## Pile V2 Stats:

- Wikipedia Dump Date: 2022-10-06
- Number of Included Articles: 6100633
- Archive Size (Jsonlines): 15.8GB