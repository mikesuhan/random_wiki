# random_wiki
Downloads the content of random Wikipedia and other MediaWiki pages and saves it as plaintext.

Included are samples of random pages from English Wikipedia, Turkish Wikipedia, and Conservapedia that were downloaded using the random_wiki.py.

# Examples

## Download .txt files and save them in 'download_folder' using default settings (defaults to Turkish Wikipedia)

from random_wiki import RandomWiki
rw = RandomWiki('download_folder')
rw.start()

## Download 100 .txt files to 'another_folder' from English Wikipedia

from random_wiki import RandomWiki
rw = RandomWiki('another_folder', limit=100, rand_url='https://en.wikipedia.org/wiki/Special:Random')
rw.start()

Note that the value of rand_url is the href of the "Random" link on the English Wikipedia homepage.
