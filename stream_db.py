from tqdm import tqdm 
from lm_dataformat import Archive
import re 
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def process_raw_article_dump(raw_text:str) -> str:
    """
    Processes raw article dump into a cleaned article string with exclusion rules taken from
    `Wiki-40B: Multilingual Language Model Dataset` 
    <https://aclanthology.org/2020.lrec-1.297/> by Guo et al. 

    Rules:
        - Non-content sections like 'Reference', 'See also', and 'External Links' sections are excluded
        - Lists, Links, images, captions and tables are excluded
        - 
    """

    title = raw_text['title']

    article_text = ""

    sections = raw_text['sections']
    for section in sections:
        # Sections from articles we exclude
        if section['title'].lower().strip() in ['references', 'see also', 'external links', 'further reading', 'sources', 'bibliography']:
            continue 

        if 'paragraphs' in section.keys():
            # skip extra sections that contain no text content (ex: lists )
            if len(section['paragraphs']) == 0:
                continue
            
            # it might occur that wtf_wikipedia parses out a section to have a paragraph with no sentences, 
            # to catch this, we just count the total number of sentences in a given paragraph
            sentence_sum = 0 
            for paragraph in section['paragraphs']:
                sentence_sum += len(paragraph['sentences'])

            if sentence_sum == 0:
                continue
            
            """
            We parse out tables and lists from the text but there are still sections of the format:

                *single short sentence*
                *list*

            For sections with a single sentence, we skip the section if the total number of words in the sentence is fewer than 5. 
            """
            if sentence_sum == 1:
                word_cnt = 0 
                for paragraph in section['paragraphs']:
                    if len(paragraph['sentences']) > 0:
                        word_cnt += len(paragraph['sentences'][0]['text'].split())
                if word_cnt < 5:
                    continue

            if len(section['title']) > 0: 
                article_text += "\n\n"+section['title']+"\n\n" 
            else:
                article_text += "\n\n"
            
            joined_paragraphs_list = []
            for paragraph in section['paragraphs']:
                joined_sentences = []
                for i in range(len(paragraph['sentences'])):
                    if len(paragraph['sentences'][i]['text']) > 0:
                        joined_sentences.append(paragraph['sentences'][i]['text'])
                if len(joined_sentences) > 0:
                    joined_paragraphs_list.append(" ".join(joined_sentences))
            if len(joined_paragraphs_list) > 0:
                joined_paragraphs = "\n\n".join(joined_paragraphs_list)
                article_text += joined_paragraphs

    return title+article_text

if __name__ == '__main__':
    import pymongo
    
    client = pymongo.MongoClient("mongodb://localhost/enwiki")

    assert 'enwiki' in client.list_database_names(), "Check to ensure Mongo is running and if enwiki table is populated"

    wiki = client['enwiki']
    assert 'pages' in wiki.list_collection_names(), "Check to ensure Mongo is running!"
    data = wiki['pages']

    with open('featured_lists.txt', 'r') as f:
        featured_lists = f.read()
    
    featured_lists = featured_lists.split('\n')

    ar = Archive('enwiki_20221006_processed')

    # Articles that start with 'List of' are Wikimedia list articles. Ignore these as they contain 'real' no content
    pattern = r"^[Ll]ist [Oo]f"
    skipped = 0 
    comitted = 0 
    for article_text in tqdm(data.find()):
        title = article_text['title']
        if re.match(pattern, title):
            if title in featured_lists:
                ar.add_data(process_raw_article_dump(article_text))
                comitted += 1
            else:
                skipped += 1
                continue
        else:
            ar.add_data(process_raw_article_dump(article_text))
            comitted += 1

    # remember to commit at the end!
    ar.commit()
    #DEBUG:__main__:Conversion Completed - Comitted Articles: 6100633 - Skipped Articles: 112952
    logger.debug(f'Conversion Completed - Comitted Articles: {comitted} - Skipped Articles: {skipped}')

 
