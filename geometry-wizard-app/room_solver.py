from dragonfly.room2d import Room2D
from ladybug_geometry.geometry3d import Vector3D
from honeybee.boundarycondition import Outdoors
from honeybee.orientation import (angles_from_num_orient, 
  orient_index)
from honeybee.room import Room
from dragonfly.windowparameter import SimpleWindowRatio

def get_rooms(height, 
    vertices, 
    n_floors,
    wwr):

    # create a base room
    # TODO: add core
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
    win_par = [SimpleWindowRatio(r) for r in wwr]
    angles = angles_from_num_orient(len(win_par))
    for room in room_2ds:
        room_win_par = []
        for bc, orient in zip(room.boundary_conditions, 
                room.segment_orientations()):
            orient_i = orient_index(orient, angles)
            win_p = win_par[orient_i] if isinstance(bc, 
                Outdoors) else None
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

    return rooms