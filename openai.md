# completions endpoint
## create completion
```python
POST https://api.openai.com/v1/engines/{engine_id}/completions
```

Path parameters
engine_id
string
Required
The ID of the engine to use for this request

```python
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Completion.create(
  engine="text-davinci-002",
  prompt="Say this is a test",
  max_tokens=5
)

# parameters
{
  "prompt": "Say this is a test",
  "suffix": "-- this comes after -- davinci",
  "max_tokens": 5, # davinci max - 4096, all other models max - 2048 tokens
  "temperature": 1, # sampling temp - higher values mean the model will take more risks (more creative)
  "top_p": 1, # alternative to sampling with temp - nucleus sampling
  "n": 1, # number of results to generate for each prompt
  "stream": false, # option to stream back partial progress
  "echo": false, # echo back prompt in addition to completion, default false
  "presence_penalty": 0, # default 0, -2 < x > 2, pos. values penalize new tokens based on whether they appear in the text so far - increase likelihood to talk about new topics
  "frequence_penalty": 0, # default 0, -2 < x > 2, pos. values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat tge same line verbatim
  "logprobs": null,
  "stop": "\n"
}

# response
{
  "id": "cmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
  "object": "text_completion",
  "created": 1589478378,
  "model": "text-davinci-002",
  "choices": [
    {
      "text": "\n\nThis is a test",
      "index": 0,
      "logprobs": null,
      "finish_reason": "length"
    }
  ]
}

```

# classifications
## create classification
```python
POST https://api.openai.com/v1/classifications

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Classification.create(
  search_model="ada",
  model="curie",
  examples=[
    ["A happy moment", "Positive"],
    ["I am sad.", "Negative"],
    ["I am feeling awesome", "Positive"]
  ],
  query="It is a raining day :(",
  labels=["Positive", "Negative", "Neutral"],
)

# parameters
{
  "examples": [
    ["A happy moment", "Positive"],
    ["I am sad.", "Negative"],
    ["I am feeling awesome", "Positive"]
  ],
  "labels": ["Positive", "Negative", "Neutral"],
  "query": "It is a raining day :(",
  "search_model": "ada",
  "model": "curie"
}

# response
{
  "completion": "cmpl-2euN7lUVZ0d4RKbQqRV79IiiE6M1f",
  "label": "Negative",
  "model": "curie:2020-05-03",
  "object": "classification",
  "search_model": "ada",
  "selected_examples": [
    {
      "document": 1,
      "label": "Negative",
      "text": "I am sad."
    },
    {
      "document": 0,
      "label": "Positive",
      "text": "A happy moment"
    },
    {
      "document": 2,
      "label": "Positive",
      "text": "I am feeling awesome"
    }
  ]
}
```

# answers
## create answer
```python
POST https://api.openai.com/v1/answers

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Answer.create(
  search_model="ada",
  model="curie",
  question="which puppy is happy?",
  documents=["Puppy A is happy.", "Puppy B is sad."],
  examples_context="In 2017, U.S. life expectancy was 78.6 years.",
  examples=[["What is human life expectancy in the United States?","78 years."]],
  max_tokens=5,
  stop=["\n", "<|endoftext|>"],
)

# parameters
{
  "documents": ["Puppy A is happy.", "Puppy B is sad."],
  "question": "which puppy is happy?",
  "search_model": "ada",
  "model": "curie",
  "examples_context": "In 2017, U.S. life expectancy was 78.6 years.",
  "examples": [["What is human life expectancy in the United States?","78 years."]],
  "max_tokens": 5,
  "stop": ["\n", "<|endoftext|>"]
}

# response
{
  "answers": [
    "puppy A."
  ],
  "completion": "cmpl-2euVa1kmKUuLpSX600M41125Mo9NI",
  "model": "curie:2020-05-03",
  "object": "answer",
  "search_model": "ada",
  "selected_documents": [
    {
      "document": 0,
      "text": "Puppy A is happy. "
    },
    {
      "document": 1,
      "text": "Puppy B is sad. "
    }
  ]
}
```

# files
files are used to upload documents that can be used accross features like Answers, Search, and Classifications

## list files
```python
GET https://api.openai.com/v1/files

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.File.list()

# response
{
  "data": [
    {
      "id": "file-ccdDZrC3iZVNiQVeEA6Z66wf",
      "object": "file",
      "bytes": 175,
      "created_at": 1613677385,
      "filename": "train.jsonl",
      "purpose": "search"
    },
    {
      "id": "file-XjGxS3KTG0uNmNOK362iJua3",
      "object": "file",
      "bytes": 140,
      "created_at": 1613779121,
      "filename": "puppy.jsonl",
      "purpose": "search"
    }
  ],
  "object": "list"
}
```

## upload file

```python
POST https://api.openai.com/v1/files

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.File.create(
  file=open("puppy.jsonl"),
  purpose='answers'
)

# response
{
  "id": "file-XjGxS3KTG0uNmNOK362iJua3",
  "object": "file",
  "bytes": 140,
  "created_at": 1613779121,
  "filename": "puppy.jsonl",
  "purpose": "answers"
}
```

delete file
```python
DELETE https://api.openai.com/v1/files/{file_id}

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.File.delete("file-XjGxS3KTG0uNmNOK362iJua3")

# response
{
  "id": "file-XjGxS3KTG0uNmNOK362iJua3",
  "object": "file",
  "deleted": true
}
```

retrieve file
```python
GET https://api.openai.com/v1/files/{file_id}

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.File.retrieve("file-XjGxS3KTG0uNmNOK362iJua3")

# response
{
  "id": "file-XjGxS3KTG0uNmNOK362iJua3",
  "object": "file",
  "bytes": 140,
  "created_at": 1613779657,
  "filename": "puppy.jsonl",
  "purpose": "answers"
}
```

## retrieve file content
```python
GET https://api.openai.com/v1/files/{file_id}/content

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
content = openai.File.download("file-XjGxS3KTG0uNmNOK362iJua3")

```

# reference links
- [openai models breakdown](https://beta.openai.com/docs/engines/overview)
  - [model comparison tool](https://gpttools.com/comparisontool)
- [openai example flask project](https://github.com/openai/openai-quickstart-python)
- [documentation](https://beta.openai.com/docs/api-reference/completions/create?lang=python)
