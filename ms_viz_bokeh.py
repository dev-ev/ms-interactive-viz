#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from bokeh.io import output_notebook, reset_output
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter, Label
from bokeh.palettes import Category10
import matplotlib.pyplot as plt


# <h2>Making mass spectra interactive with bokeh</h2>

# Visualizing peptide fragmentation mass spectra

# Import an example of a fragment ion spectrum:<br>
# a spectrum is a list of value pairs: mass-to-charge (shortened <i>m/z</i>) and inetsity of a signal for each ion

# In[2]:


df = pd.read_csv('tmt_spectrum_example.csv', sep=',')
print(df.shape)
df.head(3)


# Assign a precursor <i>m/z</i> and charge, they are often known and stored alongside the information about fragment ions

# In[3]:


precMZ = 939.88733
precCh = 5


# <h3>Take a look at a static view of the spectrum using matplotlib</h3>

# Matplotlib plots are highly customizable, which makes it the choice for preparing a publication quality spectra. The <i>stem</i> method is handy for displaying mass spectra:

# In[4]:


fig, ax = plt.subplots(1, 1, figsize=(15,4))
fig.suptitle('Peptide Fragmentation Mass Spectrum')

ax.stem( df['mz'], df['Intensity'], markerfmt=' ' )
ax.set_xlabel('m/z')
ax.set_ylabel('Intensity')


# As you can see, the typical characteristics of a tandem mass spectrum are:
# * High density of the <i>m/z</i> values, a spectrum has dozens or even hundreds of points
# * Substantial differences in the intensity (height) of the signals

# It is impossible to put all <i>m/z</i> labels onto the plot, but it is of primary interest for the scientists to see those values. An interactive highlighting of <i>m/z</i> would come very handy!

# <h3>Render bokeh plot</h3>

# In[5]:


mainTitle = 'Peptide Fragmentation Mass Spectrum'
cds = ColumnDataSource(data=df)


# In[7]:


output_notebook()


# In[8]:


#output_file('msms_tmt_bar.html')

def create_p(width=800, height=300):
    tooltips = [
        ('m/z','@mz{0.0000}'),
        ('Int','@Intensity')
        ]
    p = figure(
        plot_width=width, plot_height=height,
        title = mainTitle,
        tools = 'xwheel_zoom,xpan,box_zoom,undo,reset',
        tooltips=tooltips
        )
    return p
p = create_p()

p.vbar(
    x = 'mz', top = 'Intensity',
    source = cds,
    color = '#324ea8',# alpha = 0.8,
    width = 0.001
    )

show(p)


# But there's a problem with the bar plots: they have constant width. If we set the width to a meaningful value that is based on the actual uncertainty of the <i>m/z</i> measurement, it will be extremely narrow. And the hover tool does not work as we would want it to do! 

# In[9]:


p = figure(
    plot_width=800, plot_height=300,
    title = mainTitle
    )

p.line(
    x = 'mz', y = 'Intensity',
    source = cds,
    color = '#324ea8',# alpha = 0.8,
    line_width = 2
    )

show(p)


# Let's modify the line, so that it adopts the expected shape, but stays continuous

# In[10]:


#Triplicate the points on the m/z axis
mzTransformed = [ (x, x, x) for x in df['mz'] ]
#Flatten the list of tuples for the m/z axis
mzTransformed = [ x for y in mzTransformed for x in y ]
#Create the vertical bars for each intensity value
intensTransformed = [ (0, x, 0) for x in df['Intensity'] ]
#Flatten the list of tuples for the intensity axis
intensTransformed = [ x for y in intensTransformed for x in y ]
df2 = pd.DataFrame(
    {
        'mz': mzTransformed,
        'Intensity': intensTransformed
    }
)
df2.head(7)


# In[11]:


df2.plot(x='mz', y='Intensity', figsize=(15, 4))


# In[21]:


#output_file('msms_tmt_spectrum2.html')
cds = ColumnDataSource(data=df2)

p = create_p()

maxIntens = df2['Intensity'].max()
#Main line
p.line(
    'mz', 'Intensity',
    source = cds,
    color = '#324ea8',# alpha = 0.8,
    line_width = 2
    )
#Add the precursor info as a dashed line with a label
def add_precursor(p, mz, charge, intens, col):
    p.line(
        [mz, mz], [0, intens*0.9],
        line_dash = 'dashed', line_width = 4,
        color = col, alpha = 0.5,
        )
    p.add_layout(
        Label(
            x = mz, y = intens*0.93,
            text = f'Precursor {mz}, {charge}+',
            text_font_size = '10pt',
            text_color = col
            )
        )
add_precursor(p, precMZ, precCh, maxIntens, '#198c43')

#Format axis labels
def add_axis_labels(p):
    p.xaxis.axis_label = 'Fragment m/z'
    p.xaxis.axis_label_text_font_size = '10pt'
    p.xaxis.major_label_text_font_size = '9pt'

    p.yaxis.axis_label = 'Intensity'
    p.yaxis.axis_label_text_font_size = '10pt'
    p.yaxis.major_label_text_font_size = '9pt'
    p.yaxis.formatter = NumeralTickFormatter(format='0.')
add_axis_labels(p)

show(p)


# <h3>What if the signals are not al the same?</h3>

# Download the same spectrum with annotations

# In[17]:


dfA = pd.read_csv('tmt_spectrum_annotated.csv', sep=',')
print(dfA.shape)
dfA.head(3)


# There are 3 categories of signals:

# In[18]:


dfA['Annotation'].unique()


# In[19]:


mzTransformed = [ (x, x, x) for x in dfA['mz'] ]
mzTransformed = [ x for y in mzTransformed for x in y ]
intensTransformed = [ (0, x, 0) for x in dfA['Intensity'] ]
intensTransformed = [ x for y in intensTransformed for x in y ]
annotTransformed = [ (x, x, x) for x in dfA['Annotation'] ]
annotTransformed = [ x for y in annotTransformed for x in y ]
dfA2 = pd.DataFrame(
    {
        'mz': mzTransformed,
        'Intensity': intensTransformed,
        'Annotation': annotTransformed
    }
)
dfA2.head(7)


# In[22]:


#output_file('msms_tmt_spectrum_Cat.html')

#Create a separate ColumnDataSource for each categorical value
sources = []
for idx, cat in enumerate( dfA2['Annotation'].unique() ):
    sources.append(
        (
            idx, cat,
            ColumnDataSource(
                data=dfA2[
                    dfA2['Annotation'] == cat
                ]
            )
        )
    )
print(sources)

p = create_p()

maxIntens = dfA2['Intensity'].max()
#Create separate line for each annotation
for idxColor, cat, cds in sources:
    #Assign colors from the Category10 paletted
    #If there are more than 10 categories, the colors will start to rotate
    idxColor = idxColor % 10
    p.line(
        'mz', 'Intensity',
        source = cds,
        color = Category10[10][idxColor],
        line_width = 2, alpha = 0.7,
        legend_label=cat
    )
#Add a thick horizontal line at y=0 to make the look cleaner 
p.line(
    x = [ dfA2['mz'].min(), dfA2['mz'].max() ],
    y = [0, 0],
    color = Category10[10][0],
    line_width = 3
)
p.legend.location = 'top_right'
#Click on the legend item and the corresponding line will become hidden
p.legend.click_policy = 'hide'
p.legend.title = 'Signal Type'

add_precursor(p, precMZ, precCh, maxIntens, '#a31534')
add_axis_labels(p)

show(p)
