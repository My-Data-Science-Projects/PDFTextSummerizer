from transformers import pipeline
import torch

device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

text = '''According to the Xinhua News Agency, the quake occurred offshore and had its epicentre at a latitude of 42.8° North and a longitude of 146.4° East. As of now, there are no tsunami warnings.

According to reports, the earthquake struck Kushiro Town, Hokkaido Prefecture, at 8:08 a.m. local time (2308 GMT Wednesday) at a shallow depth off the southeast coast of the Nemuro Peninsula. It was rated a 4 on the Japanese seismic intensity scale of 7, according to the Japan Meteorological Agency.

On Hokkaido's eastern Pacific coast, the earthquake might alter tide levels by less than 20 centimetres, but damage is not a concern, it added.

While the JMA reported it as a 6.1 magnitude quake event, the United States Geological Survey (USGS) reported the quake as a magnitude 5.9 event, occurring approximately 107 kilometres southeast of Nemuro, at a depth of 14.9 kilometres.'''

print(summarizer(text, max_length=300, min_length=30, do_sample=False))