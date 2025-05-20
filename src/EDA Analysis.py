#!/usr/bin/env python
# coding: utf-8

# In[77]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# In[ ]:





# In[ ]:





# In[78]:


data = pd.read_csv("iris.csv")


# In[79]:


data.head()


# In[80]:


data.shape


# In[81]:


data.describe()


# In[84]:


data[['Column1', 'Column2', 'Column3', 'Column4', 'Column5']] = data.iloc[:, 0].str.split(',', expand=True)
data.drop(columns=[data.columns[0]], inplace=True)


# In[85]:


data.head()


# In[53]:


#Distribution of the data
data.describe()


# In[54]:


data.columns


# In[55]:


data['Column5'].unique()


# In[56]:


data['Column4'].unique()


# In[86]:


#Clean the data check if their are null values in the data
data.isnull()
data.isnull().sum()


# In[58]:


#if we have many null values
threshold = len(data) * 0.5  # Drop columns with more than 50% null values
data_cleaned = data.dropna(axis=1, thresh=threshold)


# In[59]:


data = data.drop(["Column1", "Column2"], axis = 1)


# In[60]:


data.head()


# In[68]:


#Univariant Analysis
# univariate plots
fig, ax=plt.subplots(1,2, figsize=(20, 6))
sns.histplot(data['Column3'], ax=ax[0])
ax[0].set_title("col3")
sns.histplot(data['Column4'], ax=ax[1])
ax[1].set_title("col4")
plt.ylim(0, 2500)


# In[74]:


a4_dims = (20, 7)
fig, axs = plt.subplots(ncols=3, figsize=a4_dims)
sns.scatterplot(x="Column3", y="Column4", ax=axs[0], data=data)
sns.scatterplot(x="Column3", y="Column5", ax=axs[1], data=data)
sns.scatterplot(x="Column4", y="Column5", ax=axs[2], data=data)

plt.show()


# In[ ]:




