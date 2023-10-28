#!/usr/bin/env python
# coding: utf-8

# In[58]:


import json
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import mimetypes 
import os
import pandas as pd


# In[59]:


credentials = json.load(open('credentials.json'))
API_KEY = credentials['API_KEY']
ENDPOINT = credentials['ENDPOINT']

form_recognizer_client = FormRecognizerClient(ENDPOINT,AzureKeyCredential(API_KEY))


# In[60]:


csv_file = 'files/output_form.csv'
if not os.path.isfile(csv_file):
    # Create an empty DataFrame to store the results
    df = pd.DataFrame(columns=['img_path', 'bill_type', 'bill_date', 'bill_amount'])
    df.to_csv(csv_file, index=False)
else:
    # If the file exists, append the data to the DataFrame
    df = pd.read_csv(csv_file)


# In[61]:


# Set the folder path containing the images
folder_path = "receipt_images/"

processed_images = set(df['img_path'])


# Loop through all the files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        img_path = os.path.join(folder_path, filename)

        if img_path not in processed_images:
            with open(img_path, "rb") as image_file:
                name = ""
                total = 0
                date = ""
                content_type, _ = mimetypes.guess_type(img_path)

                poller = form_recognizer_client.begin_recognize_receipts(image_file, content_type=content_type)

                results = poller.result()

                for receipt in results:
                    for name, field in receipt.fields.items():
                        if name == 'Total':
                            total = field.value
                        elif name == 'TransactionDate':
                            date = field.value
                        elif name == 'ReceiptType':
                            bill_type = field.value

                new_row = {'img_path': img_path, 'bill_type': bill_type, 'bill_date': date, 'bill_amount': total}
                df.loc[len(df)] = new_row
                processed_images.add(img_path)



# save the df as a csv file
df.to_csv('files/output_form.csv', index=False)

