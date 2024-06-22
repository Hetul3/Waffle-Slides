import os
import json
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain import hub
from langchain import PromptTemplate
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

text = """Euclid's theorem is an important result in mathematics, 
specifically in number theory. The theorem essentially states that there are an infinite 
number of prime numbers. Prime numbers are numbers that only have two factors: one and itself.
There are several proofs on this theorem, first being proven by Euclid himself in his book titled 
"Elements." A rudimentary explanation of this proof is as follows: Assume that there is a finite set 
consisting of all prime numbers. We can show that there is at least one prime number not included in this list. 
Let P be the product of all prime numbers, i.e. P = p1p2p3...pk. Then, let Q be P + 1. Then we can show that
q is prime or not. If q is prime, then q is not in the list, therefore ends the proof. If q is not prime, then 
some factor p divides q, which then, since P is a product of all p, then p divides P. If p divides P and p divides q, 
which is P + 1, then it must follow that p divides the difference of P and P + 1. However, no prime number 
divides 1, p cannot be in this list, thus a contradiction."""

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

system_organizer_prompt = """You are a slide organizer. You are given the script to a speech, and are to 
reorganize the speech so that it is presentable, under different topics. You will start by providing a title for 
the presentation. Then, a table of contents. Then, the title of a section, followed by the information from the 
script of the section, followed by the end of the section. This will be repeated for every section, until the end.
KEEP TITLES UNDER 7 WORDS. ENSURE THAT THE INFO UNDER THE TITLE IS VERY DESCRIPTIVE WITH GIVEN INFORMATION.
Try to make the info for each slide at least 5 sentences. Do not just write "detailed steps on how..." Write an actual detailed
description

Ensure to return this as a $JSON_BLOB
{{\n\
  "action": "Organize Script",
  "presentation": "The title of the slideshow, followed by each slide. This has to be formatted as a string in the following way.
  TITLE OF PRESENTATION
  |||||
  TITLE_1
  info
  #####
  TITLE_2
  info
  #####
  TITLE_3
  info
  #####
  .....
  #####
  TITLE_X
  info
  "
}}\n\
"""

human_organizer_prompt = """
Here is the script

{script}

Please turn this script into an organized presentation format
"""

organization_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=system_organizer_prompt)),
    HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['script'], template=human_organizer_prompt)),
])

llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo-0125")

organizer = (organization_prompt | llm)

response = organizer.invoke({"script": text}).content
response = response[52:]
response = response[:-3]
print(response)
# phrase = "\"presentation\": \""
# print(phrase)
# sliding_window = ""
# counter = 0
# for letter in response:
#     if len(sliding_window) == 17:
#         sliding_window = sliding_window[1:]
#     sliding_window += letter
#     if sliding_window == phrase:
#         print(counter)
#     counter += 1


