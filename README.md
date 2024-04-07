# FLATE
FLATE is a POE Bot, that can understand any video and generate questions in context to test your knowledge about a particular concept and also attempts to generate anki flash cards which updates reactively.


## Inspiration

I was recently taking a required training course on GDPR, while I was attentive throughout the video, I was only able to answer the followup Quiz with 60% correctness. And I re-did the video and took some notes, and was able to prefect score. This made me realize that - we often think we understand until we are tested and I thought it would be awesome to democratize contextual Q/A using Generative AI, on any video platform.

## Running this extension

    git clone github.com/riaz/FLATE

    conda create -n flate python=3.10

    pip install -r requirememts.txt

    pip install modal-client

    modal token new --source poe  (one-time only)

    modal deploy app.py 



## POE Bot

    https://poe.com/YoutubeQnA  


## Slides

https://docs.google.com/presentation/d/15Y8WDIhzeBedOdz_k1dznN7nZUNYGJxA8N-f5XjGWwc/edit#slide=id.gd9c453428_0_16