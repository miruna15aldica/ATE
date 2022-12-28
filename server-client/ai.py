# ------------------------------------------------------------------------------

#                            ========================
#                            ===  LICENSE NOTICE  ===
#                            ========================

# This code is provided under the MIT license.

# Copyright (c) 2022 Maria-Miruna ALDICA,
#                    Matei-Ștefan IONESCU,
#                    Valentin-Ioan VINTILĂ.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ------------------------------------------------------------------------------

#                          ============================
#                          ===  The actual program  ===
#                          ============================

import datasets
import fileinput
import io
from tqdm import tqdm
from transformers import pipeline
from transformers.pipelines.base import KeyDataset
from googlesearch import search
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import multiprocessing
import time

question_answering = pipeline("question-answering")
question = "Who wrote the C++ programming language?"

def get_urls(original_question, stop_no, urls):
    print(f"[i] Searching for answers (stop_no={stop_no})")
    true_question = f"site:en.wikipedia.org {original_question}"
    for url in search(true_question, stop=3):
        urls.append(url)

def ask_question(original_question):
    print("- - - - -")
    print("[i] Received question: ", original_question)
    # Allow the URLs search for at most 10 seconds
    manager = multiprocessing.Manager()
    urls = manager.list()
    for k in range(3, 0, -1):
        p = multiprocessing.Process(target=get_urls,
                                    name="Get URLs",
                                    args=(original_question, k, urls))
        p.start()
        p.join(10)
        if p.is_alive() == False:
            break
        else:
            p.terminate()
            p.join()

    if len(urls) == 0:
        return "Sorry, could not find any answer on Wikipedia!"
    
    text = ""
    print("[i] Found these results: ", urls)
    for url in urls:
        try:
            source = urlopen(url)
            soup = BeautifulSoup(source, features="html5lib")
        except Exception:
            print(f"[w] Could not load the content of '{url}'")
        else:
            for paragraph in soup.find_all('p'):
                text += paragraph.text

    text = re.sub(r'\[.*?\]+', '', text)
    text = text.replace('\n', ' ')

    print("[i] Coming up with an answer...", urls)
    result = question_answering(context=text, question=question)
    print("[i] ANSWER: ", result['answer'])
    print("- - - - -")
    return result['answer']
