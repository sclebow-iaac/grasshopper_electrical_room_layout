# Import necessary libraries
import Rhino
import math

# Import grasshopper treehelper
import ghpythonlib.treehelpers as th

# Define the Point class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, other_point):
        return ((self.x - other_point.x)**2 + (self.y - other_point.y)**2)**0.5
    
    def to_gh_point(self):
        return Rhino.Geometry.Point3d(self.x, self.y, 0)
    
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_gh_vector(self):
        return Rhino.Geometry.Vector3d(self.x, self.y, 0)
    
    def get_angle(self, other_vector: 'Vector') -> float: # Get the angle between two vectors
        # Calculate the angle between two vectors using the dot product formula
        dot_product = self.x * other_vector.x + self.y * other_vector.y
        
        # Calculate the magnitude of each vector
        magnitude_self = (self.x**2 + self.y**2)**0.5
        magnitude_other = (other_vector.x**2 + other_vector.y**2)**0.5
        
        # Calculate the angle in radians
        return math.acos(dot_product / (magnitude_self * magnitude_other))
    
    def rotate(self, angle: float) -> 'Vector': # Rotate the vector by a given angle in radians
        # Rotate the vector by a given angle in radians
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        new_x = self.x * cos_angle - self.y * sin_angle
        new_y = self.x * sin_angle + self.y * cos_angle
        
        return Vector(new_x, new_y)

def inches_to_feet(inches):
    return inches / 12

# Define the Door class
class Door:
    def __init__(self, width=3, height=10, position: Point = Point(0, 0), orientation: Vector = Vector(0, 1)):
        self.width = width
        self.height = height
        self.position = position
        self.orientation = orientation
        self.thickness = inches_to_feet(4) # Thickness of the door

        self.door_geometry = self.create_rhino_geometry(door=True, clearance=False)
        self.clearance_geometry = self.create_rhino_geometry(door=False, clearance=True)
        self.geometry = self.create_rhino_geometry(door=True, clearance=True)

    def create_rhino_geometry(self, door=True, clearance=True) -> Rhino.Geometry.Brep:
        # Initialize a list to store the geometry
        equipment_geometry = []
        
        if door:
            # Create a box geometry for the door
            min_x = self.position.x - self.width / 2 # min_x is the left side of the door
            max_x = self.position.x + self.width / 2 # max_x is the right side of the door
            min_y = self.position.y - self.thickness / 2 # min_y is the front side of the door
            max_y = self.position.y + self.thickness / 2 # max_y is the back side of the door
            min_z = 0 # min_z is the bottom of the door
            max_z = self.height # max_z is the top of the door

            door_brep = Rhino.Geometry.Brep.CreateFromBox(Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the door
            
            # Rotate the door 45 degrees around the Z-axis by the angle of orientation at the hinge
            rotation_axis = Rhino.Geometry.Vector3d(0, 0, 1) # Z-axis
            rotation_angle = math.pi / 4 # 45 degrees in radians

            hinge_point = Rhino.Geometry.Point3d(self.position.x + self.width / 2, self.position.y, 0) # Hinge point is the right side of the door
            door_brep.Rotate(rotation_angle, rotation_axis, hinge_point) # Rotate the door around the hinge point

            equipment_geometry.append(door_brep)
        if clearance:
            # Create clearance geometry inside the room
            min_x = self.position.x - self.width / 2
            max_x = self.position.x + self.width / 2
            min_y = self.position.y
            max_y = self.position.y + self.width
            min_z = 0
            max_z = self.height
            clearance_brep = Rhino.Geometry.Brep.CreateFromBox(Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z))
            equipment_geometry.append(clearance_brep)            
        
        # Rotate the geometry around the Z-axis by the angle of orientation
        rotation_axis = Rhino.Geometry.Vector3d(0, 0, 1) # Z-axis
        rotation_angle = self.orientation.get_angle(Vector(0, 1))
        print(f'Rotation angle: {rotation_angle}')

        if rotation_angle != 0:
            for brep in equipment_geometry:
                brep.Rotate(rotation_angle, rotation_axis, self.position.to_gh_point())

        return equipment_geometry
    
    def rotate(self, angle): # Rotate the door by a given angle in radians
        self.orientation = self.orientation.rotate(angle)
        # Update the geometry after rotation
        self.door_geometry = self.create_rhino_geometry(door=True, clearance=False)
        self.clearance_geometry = self.create_rhino_geometry(door=False, clearance=True)
        self.geometry = self.create_rhino_geometry(door=True, clearance=False)

# Define the ElectricalEquipment base class
class ElectricalEquipment:
    def __init__(self, width, height, depth, position: Point = Point(0, 0), front_clearance=3, side_clearance=0, rear_clearance=0, orientation: Vector = Vector(0, 1)):
        self.width = width
        self.height = height
        self.depth = depth
        self.position = position
        # Add attributes for clearances
        self.front_clearance = front_clearance
        self.side_clearance = side_clearance
        self.rear_clearance = rear_clearance

        self.orientation = orientation

        self.clearance_geometry = self.create_rhino_geometry(clearance=True, equipment=False)
        self.equipment_geometry = self.create_rhino_geometry(equipment=True, clearance=False)
        self.geometry = self.create_rhino_geometry(equipment=True, clearance=True)

    def place(self):
        # Logic to place the equipment in the room
        pass

    def rotate(self, angle): # Rotate the equipment by a given angle in radians
        self.orientation = self.orientation.rotate(angle)
        # Update the geometry after rotation
        self.clearance_geometry = self.create_rhino_geometry(clearance=True, equipment=False)
        self.equipment_geometry = self.create_rhino_geometry(equipment=True, clearance=False)
        self.geometry = self.create_rhino_geometry(equipment=True, clearance=True)
        

    def create_rhino_geometry(self, equipment=True, clearance=True) -> Rhino.Geometry.Brep:
        # Create a box geometry for the equipment
        # Width should be centered at the position
        min_x = self.position.x - self.width / 2 # min_x is the left side of the equipment
        max_x = self.position.x + self.width / 2 # max_x is the right side of the equipment
        min_y = self.position.y + self.rear_clearance # min_y is the rear side of the equipment (rear clearance is added)
        max_y = self.position.y + self.depth + self.rear_clearance # max_y is the front side of the equipment (depth + rear clearance)
        min_z = 0 # min_z is the bottom of the equipment
        max_z = self.height # max_z is the top of the equipment
        if equipment: # If equipment is True, create the equipment geometry
            equipment_brep = Rhino.Geometry.Brep.CreateFromBox(
                Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the equipment
        
        # Create clearance geometry
        if clearance:
            clearance_brep_list = [] # Initialize a list to store clearance geometry
            if self.front_clearance > 0: 
                # Create a box geometry for the front clearance
                # front_clearance should be along the positive y-axis and offset from the equipment
                min_x = self.position.x - self.width / 2 # min_x is the left side of the equipment
                max_x = self.position.x + self.width / 2 # max_x is the right side of the equipment
                min_y = self.position.y + self.depth + self.rear_clearance # min_y is the front side of the equipment
                max_y = self.position.y + self.depth + self.front_clearance + self.rear_clearance # max_y is the front side of the equipment + front clearance
                min_z = 0 # min_z is the bottom of the equipment
                max_z = self.height # max_z is the top of the equipment
                front_clearance_brep = Rhino.Geometry.Brep.CreateFromBox(
                    Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the front clearance
                clearance_brep_list.append(front_clearance_brep)

            if self.side_clearance > 0:
                # Create a box geometry for the left side clearance
                # side_clearance should be along the negative x-axis and offset from the equipment
                min_x = self.position.x - self.width / 2 - self.side_clearance # min_x is the left side of the equipment - side clearance
                max_x = self.position.x - self.width / 2 # max_x is the left side of the equipment
                min_y = self.position.y + self.rear_clearance # min_y is the rear side of the equipment
                max_y = self.position.y + self.depth + self.rear_clearance # max_y is the front side of the equipment
                min_z = 0 # min_z is the bottom of te equipment
                max_z = self.height # max_z is the top of the equipment
                left_clearance_brep = Rhino.Geometry.Brep.CreateFromBox(
                    Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the left side clearance

                # Create a box geometry for the right side clearance
                # side_clearance should be along the positive x-axis and offset from the equipment
                min_x = self.position.x + self.width / 2 # min_x is the right side of the equipment
                max_x = self.position.x + self.width / 2 + self.side_clearance # max_x is the right side of the equipment + side clearance
                min_y = self.position.y + self.rear_clearance # min_y is the rear side of the equipment
                max_y = self.position.y + self.depth + self.rear_clearance # max_y is the front side of the equipment
                min_z = 0 # min_z is the bottom of the equipment
                max_z = self.height # max_z is the top of the equipment
                # Create a box geometry for the right side clearance
                right_clearance_brep = Rhino.Geometry.Brep.CreateFromBox(
                    Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) 

                clearance_brep_list.append(left_clearance_brep)
                clearance_brep_list.append(right_clearance_brep)

            if self.rear_clearance > 0: # If rear clearance is greater than 0
                # Create a box geometry for the rear clearance
                # rear_clearance should be along the negative y-axis and offset from the equipment
                min_x = self.position.x - self.width / 2 # min_x is the left side of the equipment
                max_x = self.position.x + self.width / 2 # max_x is the right side of the equipment
                min_y = self.position.y # min_y is the wall 
                max_y = self.position.y + self.rear_clearance # max_y is the rear side of the equipment
                min_z = 0
                max_z = self.height
                rear_clearance_brep = Rhino.Geometry.Brep.CreateFromBox(
                    Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z))
            
                clearance_brep_list.append(rear_clearance_brep)

        equipment_geometry = []
        if equipment:
            equipment_geometry.append(equipment_brep)
        if clearance:
            for clearance_brep in clearance_brep_list:
                equipment_geometry.append(clearance_brep)

        # Rotate the geometry around the Z-axis by the angle of orientation
        rotation_axis = Rhino.Geometry.Vector3d(0, 0, 1) # Z-axis
        # Angle in radians
        rotation_angle = self.orientation.get_angle(Vector(0, 1)) 
        
        print(f'Rotation angle: {rotation_angle}')

        if rotation_angle != 0:
            for brep in equipment_geometry:
                brep.Rotate(rotation_angle, 
                            rotation_axis, self.position.to_gh_point())
        
        # Return the combined geometry
        return equipment_geometry

# Define the Panelboard subclass
class Panelboard(ElectricalEquipment):
    
    def __init__(self, width=2, height=4, depth=0.5, 
                 position: Point = Point(0, 0)):
        super().__init__(width, height, depth, position)
        # Additional attributes specific to panelboard
        # ...

# Define the Transformer subclass
class Transformer(ElectricalEquipment):
    def __init__(self, width=3, height=3, depth=3, 
                 position: Point = Point(0, 0)):
        self.rear_clearance = 0.25
        self.front_clearance = 3
        self.side_clearance = 0.25

        super().__init__(width, height, depth, position, 
                         self.front_clearance, self.side_clearance, 
                         self.rear_clearance)

# Define the ElectricalRoom class
class ElectricalRoom:
    # Initialize the electrical room with necessary attributes (e.g., dimensions, list of equipment)
    # ...
    def __init__(self, width, length, height=10, door_count=1):
        self.width = width
        self.length = length
        self.height = height
        self.door_count = door_count
        self.equipment_list = []

        self.doors = [Door() for _ in range(door_count)]

        self.interior_rectangle = self.create_interior_rectangle()
        self.wall_geometry = self.create_wall_geometry()
    
    # Method to add equipment to the room
    def add_equipment(self, equipment: ElectricalEquipment, count=1) -> bool:
        for i in range(count):
            self.equipment_list.append(equipment)
        return True
    
    def create_interior_rectangle(self) -> Rhino.Geometry.Rectangle3d:
        # Create a rectangle for the room
        min_x = -self.width / 2
        max_x = self.width / 2
        min_y = -self.length / 2
        max_y = self.length / 2

        return Rhino.Geometry.Rectangle3d(Rhino.Geometry.Plane.WorldXY, 
                                           Rhino.Geometry.Point3d(min_x, min_y, 0), 
                                           Rhino.Geometry.Point3d(max_x, max_y, 0))
    
    def create_exterior_rectangle(self, wall_thickness) -> Rhino.Geometry.Rectangle3d:
        # Create a rectangle for the room
        min_x = -self.width / 2 - wall_thickness
        max_x = self.width / 2 + wall_thickness
        min_y = -self.length / 2 - wall_thickness
        max_y = self.length / 2 + wall_thickness

        return Rhino.Geometry.Rectangle3d(Rhino.Geometry.Plane.WorldXY,
                                           Rhino.Geometry.Point3d(min_x, min_y, 0), 
                                           Rhino.Geometry.Point3d(max_x, max_y, 0))

    # Method to create the wall geometry of the room
    # def create_wall_geometry(self) -> Rhino.Geometry.Brep:
    def create_wall_geometry(self):
        wall_thickness = 0.5 # Thickness of the wall

        # Offset the interior rectangle to create the exterior rectangle
        interior_rectangle = self.interior_rectangle
        exterior_rectangle = self.create_exterior_rectangle(wall_thickness)

        edges = [interior_rectangle.ToNurbsCurve(), exterior_rectangle.ToNurbsCurve()]
        # Create a surface from both rectangles
        surface = Rhino.Geometry.Brep.CreatePlanarBreps(edges, 0.001)[0]

        # Extrude the surface to create the walls
        direction = Rhino.Geometry.Vector3d(0, 0, self.height)
        wall_brep = Rhino.Geometry.Brep.CreateFromOffsetFace(surface.Faces[0], self.height, 0.001, True, True)

        return wall_brep
        

# Create an instance of ElectricalRoom
# INPUTS
# Dimensions of the room
room_width = 20
room_length = 30
room_height = 10
door_count = 1

electrical_room = ElectricalRoom(room_width, room_length,
                                    room_height, door_count)

# Create instances of Panelboard and Transformer
# INPUTS
panelboard_count = 2
transformer_count = 1

# Add the panelboard and transformer to the electrical room
# ...
# electrical_room.add_equipment(Panelboard(), panelboard_count)
electrical_room.add_equipment(Transformer(), transformer_count)

first_equipment = electrical_room.equipment_list[0]
first_equipment.rotate(math.pi / 2) # Rotate the first equipment by 90 degrees

equipment_geometry = []
clearance_geometry = []
all_equipment_geometry = []

# Loop through each equipment in the room and create its geometry
for equipment in electrical_room.equipment_list:
    print(equipment)
    equipment_geometry.append(equipment.equipment_geometry)
    clearance_geometry.append(equipment.clearance_geometry)
    all_equipment_geometry.append(equipment.geometry)

equipment_geometry = []
clearance_geometry = []
all_equipment_geometry = []

door_0 = Door()
door_0.rotate(math.pi / 2)

equipment_geometry.append(door_0.door_geometry)
clearance_geometry.append(door_0.clearance_geometry)
all_equipment_geometry.append(door_0.geometry)

output = electrical_room.wall_geometry

# equipment_geometry the geometry to Grasshopper
equipment_geometry = th.list_to_tree(equipment_geometry)
clearance_geometry = th.list_to_tree(clearance_geometry)
all_equipment_geometry = th.list_to_tree(all_equipment_geometry)

