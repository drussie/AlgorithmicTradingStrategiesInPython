from openbb.sdk import openbb

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# Replace YOUR_API_KEY with your actual OpenAI API key.
API_KEY = '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'

llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=API_KEY)  # Pass the API key directly here

prompt = """
Is the predominant sentiment in the following text positive, negative, or neutral?
-----------------------------------
Statement: {statement}
-----------------------------------
Respond with one word in lowercase: positive, negative, or neutral.
Sentiment:
"""

chain = LLMChain.from_string(
    llm=llm,
    template=prompt
)

tsla = openbb.news(term="tsla")
tsla["Sentiment"] = tsla.Description.apply(chain.run)
