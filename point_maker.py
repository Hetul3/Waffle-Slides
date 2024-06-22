import os, json, ast, re
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

text = """To live, or not to live: that is the question. Is it more noble to put up with all the difficulties that fate throws our way, or to fight against them, and, in fighting them, put an end to everything? Death is like sleeping, that's all. A kind of sleep that ends the countless heartaches and sufferings that are part of life – now that's something to be desired. To die, to sleep – and during this sleep, maybe we dream.

But that's the problem. In that sleep-like death, when we've finally been released from this painful life, who knows what dreams we'll have? That's enough to make us hesitate, to keep on suffering, and to put up with a horrible existence for so long. Otherwise, who would put up with the slaps and insults we endure over time, the wrongs done to us by the powerful, the arrogance of proud men, the heartaches of rejected love, the bureaucracy in the courts, the rudeness of bureaucrats, and the offenses dished out by unworthy people, that we patiently accept– when we could just settle our account with God by using a dagger on ourselves?

Who would carry these heavy burdens, grunting and sweating under an exhausting life, if it weren't for the fear of something worse in the afterlife, that unknown country from whose border nobody ever returns? This fear bewilders us, and makes us prefer the troubles we know, rather than run off to troubles we don't know. In the end, contemplating the afterlife makes us cowards, and the bright color of our bravery is turned pale by our contemplation. And all our ambitious plans get put on hold while we think about this, and end up never being executed."""

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

system_points_prompt = """You are a point maker. You are given an input in the following form

TITLE OF PRESENTATION
|||||
Title of Slide
Info of slide 
#####
Title of Slide 2
Info of slide 2
#####
...
#####
Title of Slide X
Info of slide X
#####

You are to turn the INFO of each slide into a couple of bullet points fit for a google slide presentation. 
You are to output in a $JSON_BLOB
{{\n\
    "action": "Make Points",
    "point presentation": "Return the presentation in a list format like so: [Title of Presentation, [Title of Slide 1, Point 1 of Slide 1, Point 2 of Slide 1, Point 3 of Slide 1..], [Title of Slide 2, Point 1 of Slide 2, Point 2 of Slide 2,...],...,[Title of Slide X, Point 1 of Slide X, Point 2 of Slide X, ..., Point X of Slide X]]."
}}\n\
"""

human_points_prompt="""Here is the presentation:

{presentation}

Please turn it into a point format list and return it
"""

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

point_maker_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=system_points_prompt)),
    HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['presentation'], template=human_points_prompt)),
])

llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo-0125")

organizer = (organization_prompt | llm)
point_maker = (point_maker_prompt | llm)

def extract_outermost_list(pres_list):
    start = -1
    open_brackets = 0

    for i, char in enumerate(pres_list):
        if char == '[':
            if open_brackets == 0:
                start = i
            open_brackets += 1
        elif char == ']':
            open_brackets -= 1
            if open_brackets == 0:
                end = i + 1
                return pres_list[start:end]

    return None

response = organizer.invoke({"script": text}).content

response = response[52:]
response = response[:-3]



extracted_list = []
pres_list = point_maker.invoke({"presentation": response}).content
extracted_list = extract_outermost_list(pres_list)
print("Extracted List", extracted_list)
parsed_list = ast.literal_eval(extracted_list)

# Printing out in terminal for visual pleasure
final_list = []
first = True
first_mini = True
idx = 0
first = True
first_mini = True
for value in parsed_list:
    if first:
        print("\n")
        print(value)
        print("\n")
        first = False
    elif not first:
        for point in value:
            if first_mini:
                print("\n")
                print(point)
                print("\n")
                first_mini = False
            else:
                print(f"- {point}")
    first_mini = True



