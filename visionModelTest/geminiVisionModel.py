from google.genai import types
from google import genai


client = genai.Client(api_key="AIzaSyAt59WZAmoN2FVj_FZM6wYvAdJa5Q3MFL0")
# client = genai.Client(api_key="408dd71674a433cf696bb5109e8e2a183b211b02")


with open('/home/arpit/dataCollection/collectedImages/_StoneWash__Car_Care_Center__818_Paris_Rd__Mayfield__KY__42066/ChIJP4czgyoweogRwvkgFMe5lIY.png', 'rb') as f:
    image_bytes = f.read()

response = client.models.generate_content(
model='gemini-2.5-flash-preview-04-17',
contents=[
    types.Part.from_bytes(
    data=image_bytes,
    mime_type='image/jpeg',
    ),
    # 'This is a satellite image of a car wash, decide whether it has tunnel wash facility or not. A tunnel is a rectangular like structure with clear entry and exit points for a car drive-through. The response should always begin with a "Yes," or a "No," so that a "," can be used for spilitting.'
    '''
Classify a location as a “Competitor” if any of the following conditions are true:
Tunnel Wash Structure Identified


The image contains a long, narrow building that appears to function as a tunnel car wash.


The tunnel must have:


A clear entry and exit point, located at opposite narrow ends of the structure.


Possible wet patches or visible runoff on the pavement at the exit, indicating frequent vehicle washing.


Name Contains Competitive Keywords


If the car wash’s visible signage, label, or metadata includes any of the following words, it should be classified as a competitor:


"express"


"exterior"


"full serve"


"flex serve"


Vacuum Station Presence (Optional)


The image may show a vacuum station (typically small bays or rows with hoses/canisters), but this is not a requirement for classification.


If present, include it as a supportive detail.





Response Format:

Classification: Competitor / Not a Competitor

Justification:
- [Describe what structural or textual elements were identified that led to your classification.]
- [Mention if tunnel was detected, entry/exit presence, wet area, keyword in name, vacuum station, etc.]


Instructions:
Use all available visual cues (building layout, road markings, pavement conditions, signage) and any textual data or labels included with the image to make an informed judgment.

'''
]
)

print(response.text)
