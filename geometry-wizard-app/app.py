import json
import streamlit as st
from PIL import Image
from honeybee.model import Model
from pollination_streamlit_io import ( button,
    inputs )
from ladybug_geometry.geometry2d import Point2D

from room_solver import get_rooms

'''
NOTES: it uses SI unit system (Meters) but you can edit it.
'''

# show image
# TODO: add other shapes
shapes = {
        'L-shape': './assets/l-shape.png',
    }
option = st.selectbox("Select a shape to start with:",  
    shapes.keys())
image = Image.open(shapes[option])
st.image(image, caption=option)

# values
vertices = []

if option == 'L-shape':
    a = st.number_input(
      "Segment A",
      min_value=1.0,
      max_value=9999999.0,
      value=20.0, 
      step=0.1,
      format="%f",
      key="l-shape-a")
    b = st.number_input(
      "Segment B",
      min_value=1.0,
      max_value=9999999.0,
      value=8.0, 
      step=0.1,
      format="%f",
      key="l-shape-b")
    c = st.number_input(
      "Segment B",
      min_value=1.0,
      max_value=9999999.0,
      value=8.0, 
      step=0.1,
      format="%f",
      key="l-shape-c")
    d = st.number_input(
      "Segment D",
      min_value=1.0,
      max_value=9999999.0,
      value=20.0, 
      step=0.1,
      format="%f",
      key="l-shape-d")
    
    # input validation
    if a <= c:
      c = a
      st.warning('A must be > C')
    if d <= b:
      b = d
      st.warning('D must be > B')
    
    vertices = [
      Point2D(0,0), 
      Point2D(a,0),
      Point2D(a,b),
      Point2D(c,b),
      Point2D(c,d),
      Point2D(0,d)
    ]

# generic info
n_floors = st.number_input(
    "Floors Number",
    min_value=1,
    max_value=999,
    value=2, 
    step=1,
    key="num-floor")

height = st.number_input(
    "Floor Height",
    min_value=3,
    max_value=999,
    value=4, 
    step=1,
    key="floor-height")

# room info
n_window = st.slider(label='WWR - North',
    min_value=0.00, 
    max_value=0.95, 
    step=0.05, 
    value=0.35)

e_window = st.slider(label='WWR - East',
    min_value=0.00, 
    max_value=0.95, 
    step=0.05, 
    value=0.35)

s_window = st.slider(label='WWR - South',
    min_value=0.00, 
    max_value=0.95, 
    step=0.05, 
    value=0.35)
  
w_window = st.slider(label='WWR - West',
    min_value=0.00, 
    max_value=0.95, 
    step=0.05, 
    value=0.35)

wwr = [n_window, e_window, 
    s_window, w_window]

# get rooms
rooms = get_rooms(height=height, 
    vertices=vertices, 
    n_floors=n_floors,
    wwr=wwr)

# generate hbmodel
identifier = "my-streamlit-model"
my_model = Model(identifier=identifier,
    rooms=rooms,
    units='Meters')

# rhino integration!
query = st.experimental_get_query_params()
platform = query['__platform__'][0] if '__platform__' in query else 'web'

if platform == 'Rhino':
    # rhino preview
    inputs.send(data=my_model.to_dict(),
        uniqueId='model-preview',
        defaultChecked=True,
        isPollinationModel=True,
        label='Model Preview')
    
    # rhino bake
    button.send('BakePollinationModel',
            my_model.to_dict(), 'baked-model', 
            key='baked-model')
else:
    st.download_button(
        label='Download HBJSON',
        data=json.dumps(my_model.to_dict()),
        file_name='my_model.hbjson')