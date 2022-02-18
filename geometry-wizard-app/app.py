import streamlit as st
from dragonfly.room2d import Room2D
from ladybug_geometry.geometry2d import Point2D
from ladybug_geometry.geometry3d import Vector3D
from honeybee.boundarycondition import Outdoors
from honeybee.orientation import (angles_from_num_orient, 
  orient_index)
from honeybee.room import Room
from dragonfly.windowparameter import SimpleWindowRatio
from honeybee.model import Model
from pollination_streamlit_io import button
from PIL import Image

# show image
shapes = {
    'L-shape': './assets/l-shape.png',
}
option = st.selectbox("Select a shape to start with:",  shapes.keys())
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

# generic

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

# create a base room
# todo: add core
identifier = "base-room"
floor_height=0
floor_to_ceiling_height=height

base_room = Room2D.from_vertices(
  identifier=identifier,
  vertices=vertices,
  floor_height=floor_height,
  floor_to_ceiling_height=floor_to_ceiling_height,
  is_ground_contact=True,
  is_top_exposed=True
)

# intersect and solve adjacency
room_2ds = [base_room]
room_2ds = Room2D.intersect_adjacency(room_2ds)
adj_info = Room2D.solve_adjacency(room_2ds)

# add apertures
win_ratios = [0.1, 0.2, 0.3, 0.4]

win_par = [SimpleWindowRatio(r) for r in win_ratios]
angles = angles_from_num_orient(len(win_par))
for room in room_2ds:
    room_win_par = []
    for bc, orient in zip(room.boundary_conditions, room.segment_orientations()):
        orient_i = orient_index(orient, angles)
        win_p = win_par[orient_i] if isinstance(bc, Outdoors) else None
        room_win_par.append(win_p)
    room.window_parameters = room_win_par

# get honeybee rooms
hb_rooms = [r.to_honeybee()[0] for r in room_2ds]

# many rooms
rooms = []
z = 0
for i in range(n_floors):
  z = (i * height)
  vec = Vector3D(0,0,z)
  for room in hb_rooms:
    copy_room = room.duplicate()
    copy_room.add_prefix(str(i) + '_')
    copy_room.move(vec)
    rooms.append(copy_room)

# solve adjacency with honeybee
adj_info = Room.solve_adjacency(rooms)

# generate hbmodel
identifier = "my-streamlit-model"
my_model = Model(identifier=identifier,
  rooms=rooms,
  units='Meters')

# rhino integration!
query = st.experimental_get_query_params()
platform = query['__platform__'][0] if '__platform__' in query else 'web'

if platform == 'Rhino':
  button.send('BakePollinationModel',
          my_model.to_dict(), 'my-secret-key', 
          key='my-secret-key')