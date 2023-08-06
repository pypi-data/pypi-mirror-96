# word2lex

word2lex is a simple wrapper to perform sentiment analysis with dictionaries (lexicons) automatically induced from seed words using word embeddings. 

The dictionaries were conceived for studying transcripts of parliamentary speeches, where some expressions are domain-specific and the register differs from casual English. Although designed with political texts in mind, the library should be useful for studying contexts where the language is more formal - e.g. the news media, press releases. 
 
The wrapper builds upon the [VADER library for Python](https://github.com/cjhutto/vaderSentiment) to account for valence shifting and amplifiers. 

Installation 
--------

```
pip install word2lex
```

Usage 
--------
```
from word2lex import Word2Lex

dictionary = Word2Lex()
```
The Word2Lex class creates an instance of a sentiment dictionary, with a 'sentiment' method returning a score between -1 (negative valence) and 1 (positive valence) for a text input. 

The default dictionary uses a combination of parliamentary records from three English speaking countries to train the embeddings (Britain, Canada, USA).

To compute sentiment:
```
example = 'This is a fantastic opportunity for our government.'
print(dictionary.sentiment(example))

0.4331
```

Usage should be intuitive with other data types, e.g.:
```
mylist = ['This is a fantastic opportunity for our government.', 'I oppose this bill.']
sentiment_scores = [dictionary.sentiment(x) for x in mylist]
print(sentiment_scores)

[0.4331, -0.2829]
```

Available dictionaries:
```
dictionary = Word2Lex('canada') # attuned to Canadian debates
dictionary = Word2Lex('usa') # attuned to American debates
dictionary = Word2Lex('britain') # attuned to British debates
dictionary = Word2Lex('politics_en') # the default, trained on corpora from the three countries
dictionary = Word2Lex('news_media') # trained on the Google News corpus and attuned to news media.
dictionary = Word2Lex('twitter') # trained on the Glove Twitter corpus and attuned to casual English.
```

Evaluation
--------

A forthcoming paper (Cochrane et al., 2021) compares the performance of this approach relative to other popular sentiment dictionaries.  The findings show that sentiment dictionaries induced using word embeddings achieve better accuracy when evaluated against human judgement.

The table below compares accuracy for different training corpora, evaluated on a sample of 1,020 human annotated speech transcripts from the Canadian House of Commons. The annotations are based on an 11-point valence scale, and the procedure used by human coders is described further in the reference listed below. Note that the current library includes conveniences such as valence shifting, additional corpora, and text length normalization.  The results may differ slightly from the cases examined in the paper.

| Model        |  Training Corpus                 | Accuracy (%)  |    R<sup>2</sup>  |
| -------------|----------------------------------|:-------------:|:----------:|
| britain      | British Hansard (1987-2014)      |   71.275%     |   0.345    |
| canada       | Canadian Hansard (1988-2018)     |   76.569%     |   0.476    |
| news_media   | word2vec Google News Corpus      |   75.490%     |   0.425    |
| politics_en  | britain, canada & usa combined   |   77.647%     |   0.420    |
| usa          | Congressional Record (1987-2016) |   72.843%     |   0.323    |
| twitter      | GloVe Twitter Corpus             |   63.627%     |   0.276    |

This table illustrates the impact of the source corpus used to train the embeddings. Unsurprisingly, source political corpora lead to sentiment dictionaries that are better attuned to the expected tone of political speeches. The pretrained Google News corpus works reasonably well for a task involving political texts from Canada, suggesting that these domains are similar in register. Accuracy drops when using a source corpus from social media. Conversely, the political models may not generate intuitive results in a different setting (e.g. a study on social media). 

Credits
-------

If using these materials, please cite:

Cochrane, Christopher, Ludovic Rheault, Jean-François Godbout, Tanya Whyte, Michael Wong and Sophie Borwein.  2021. "The Automatic Analysis of Emotion in Political Speech Based on Transcripts" *Political Communication*, Forthcoming.

This library is a simplified version of an implementation accounting for parts of speech and word lemmas, available [here](https://github.com/lrheault/emotion).

[Rheault, Ludovic, Kaspar Beelen, Christopher Cochrane and Graeme Hirst. 2016. "Measuring Emotion in Parliamentary Debates with Automated Textual Analysis". *PLoS ONE* 11(12): e0168843.](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0168843) 

License 
-------

This software library comes with no warranty of appropriateness for a specific purpose.

Free software: MIT license
