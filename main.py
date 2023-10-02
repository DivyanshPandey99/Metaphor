import openai
from metaphor_python import Metaphor
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi


SEC_KEY = '' # Enter Your Secret Key Here
PUB_KEY = '' # Enter Your Public Key Here
BASE_URL = 'https://paper-api.alpaca.markets/' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL) # For real trading, don't enter a base_url

openai.api_key = "OPENAI_KEY"

metaphor = Metaphor("METAPHOR KEY")

USER_QUESTION = "What are the best stocks to buy long-term right now"

SYSTEM_MESSAGE = "You are a helpful assistant that generates search queiries based on user questions. Only generate one search query."

# To make query better
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": USER_QUESTION},
    ],
)


# Get date of last week

# Get the current date
current_date = datetime.now()

# Calculate the date one week ago
one_week_ago = current_date - timedelta(days=7)

# Format the date as "yy-mm-dd"
last_week_date = one_week_ago.strftime("%y-%m-%d")


query = completion.choices[0].message.content
search_response = metaphor.search(
    query,
    num_results=10, 
    use_autoprompt=True, 
    start_published_date=last_week_date
)
print(f"URLs: {[result.url for result in search_response.results]}\n")

contents_result = search_response.get_contents()

all_symbols = {} # To store the frequency of symbols from all the urls

for i in range(10):
    # Summarize content of current url
    cur_result = contents_result.contents[i]

    SYSTEM_MESSAGE = "You are a helpful assistant that summarizes the content of a webpage. Summarize the users input."

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": cur_result.extract},
        ],
    )

    summary = completion.choices[0].message.content
    print(f"Summary for {cur_result.title}: {summary}")

    # Find the stock symbols from summary

    SYSTEM_MESSAGE = "You are a helpful assistant that finds the stock symbols in the user input which are positively talked about. Find the positive talked about stock symbols(capitalized) and write them all one blank spaced."

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": summary},
        ],
    )

    chatgpt_symbols = completion.choices[0].message.content

    symbols = chatgpt_symbols.split()

    # loop to put stock symbols in dictionary, with handling edge cases
    for symbol in symbols:
        if( not symbol or symbol.isspace()):
            continue
        if symbol in all_symbols:
            all_symbols[symbol] +=1
        else:
            all_symbols.update({symbol: 1})


# Sorting the dictionary of all symbols in reverse order (Max first)
all_symbols = sorted(all_symbols.items(), key=lambda x:x[1])
all_symbols.reverse()


symbols = []
# Taking top 5 stocks from this list
for i in range(min(len(all_symbols),5)):
    symbols.append(all_symbols[i][0])



# But the top 5 stocks
for symbol in symbols:
    api.submit_order(
        symbol=symbol, 
        qty=1,
        side='buy',
        type='market', 
        time_in_force='gtc' # Good 'til cancelled
    )












