#### About:

`joke` Is a Python Wrapper that can deliver jokes to you.

#### Quickstart:

To grab the random 10 jokes, You can use joke.joke.joke.random_10
```python
from joke import joke

result = joke.random_10() #Returns a list of dicts

for item in result: #Irritating through the list, now it returns a dict
    print(item["question"]) #Prints the joke question
    print(item["answer"]) #Prints the joke answer
    print(item["type"]) #Print the type of the joke.
```

To grab 1 random joke, You can use joke.joke.joke.random
```python
from joke import joke

result = joke.random() #Returns a dict with key value "question", "answer" and "type"

print(result["question"]) #Prints the joke question
print(result["answer"]) #Prints the joke answer
print(result["type"]) #Print the type of the joke
```

It can also be used in the command line.
```sh
>>> unknown@unknown % joke
Question: Why did the man run around his bed?
Answer: Because he was trying to catch up on his sleep!
Type: general
```

### Installing:
```
pip install -U joke
```