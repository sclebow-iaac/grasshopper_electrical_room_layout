# Import necessary libraries
import Rhino
import math
import random

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
    def __init__(self, width=3, height=inches_to_feet(80), position: Point = Point(0, 0), orientation: Vector = Vector(0, 1)):
        self.width = width
        self.height = height
        self.position = position
        self.orientation = orientation
        self.thickness = inches_to_feet(4) # Thickness of the door

        self.door_geometry = self.create_rhino_geometry(door=True, clearance=False)
        self.clearance_geometry = self.create_rhino_geometry(door=False, clearance=True)
        self.geometry = [self.door_geometry, self.clearance_geometry]
        self.void = self.create_rhino_void_geometry()

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
            
            # Rotate the door 85 degrees around the Z-axis by the angle of orientation at the hinge
            rotation_axis = Rhino.Geometry.Vector3d(0, 0, 1) # Z-axis
            rotation_angle = math.radians(135) # Rotate the door 85 degrees

            hinge_point = Rhino.Geometry.Point3d(self.position.x + self.width / 2, self.position.y - self.thickness, 0) # Hinge point is the right side of the door
            door_brep.Rotate(rotation_angle, rotation_axis, hinge_point) # Rotate the door around the hinge point

            equipment_geometry.append(door_brep)
            # print('Door geometry created')
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
            # print('Clearance geometry created')
        
        # Rotate the geometry around the Z-axis by the angle of orientation
        rotation_axis = Rhino.Geometry.Vector3d(0, 0, 1) # Z-axis
        rotation_angle = self.orientation.get_angle(Vector(0, 1))
        # print(f'Rotation angle: {rotation_angle}')

        if self.orientation.x == 1 and self.orientation.y == 0:
            # print('Orientation is 1, 0')
            rotation_angle = math.radians(-90)

        if rotation_angle != 0:
            for brep in equipment_geometry:
                brep.Rotate(rotation_angle, rotation_axis, self.position.to_gh_point())

        return equipment_geometry
    
    def create_rhino_void_geometry(self) -> Rhino.Geometry.Brep:
        # Create a box geometry for the door
        wall_thickness = 0.5 # Thickness of the wall
        min_x = self.position.x - self.width / 2
        max_x = self.position.x + self.width / 2
        min_y = self.position.y - wall_thickness
        max_y = self.position.y 
        min_z = 0
        max_z = self.height
        door_brep = Rhino.Geometry.Brep.CreateFromBox(Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the door

        # Rotate the geometry around the Z-axis by the angle of orientation
        rotation_axis = Rhino.Geometry.Vector3d(0, 0, 1) # Z-axis
        rotation_angle = self.orientation.get_angle(Vector(0, 1))

        if self.orientation.x == 1 and self.orientation.y == 0:
            # print('Orientation is 1, 0')
            rotation_angle = math.radians(-90)

        print(f'self.orientation: {self.orientation.x}, {self.orientation.y}')
        # print(f'Rotation angle: {rotation_angle}')

        if rotation_angle != 0:
            door_brep.Rotate(rotation_angle, rotation_axis, self.position.to_gh_point())

        return door_brep
    
    def rotate(self, angle): # Rotate the door by a given angle in radians
        self.orientation = self.orientation.rotate(angle)
        # Update the geometry after rotation
        self.door_geometry = self.create_rhino_geometry(door=True, clearance=False)
        self.clearance_geometry = self.create_rhino_geometry(door=False, clearance=True)
        self.geometry = [self.door_geometry, self.clearance_geometry]
        self.void = self.create_rhino_void_geometry()

    def orient(self, vector: Vector): # Orient the door to a given vector
        self.orientation = vector
        # Update the geometry after rotation
        self.door_geometry = self.create_rhino_geometry(door=True, clearance=False)
        self.clearance_geometry = self.create_rhino_geometry(door=False, clearance=True)
        self.geometry = [self.door_geometry, self.clearance_geometry]
        self.void = self.create_rhino_void_geometry()

    def set_position(self, position: Point): # Set the position of the door
        self.position = position
        # Update the geometry after rotation
        self.door_geometry = self.create_rhino_geometry(door=True, clearance=False)
        self.clearance_geometry = self.create_rhino_geometry(door=False, clearance=True)
        self.void = self.create_rhino_void_geometry()

# Define the ElectricalEquipment base class
class ElectricalEquipment:
    def __init__(self, width, height, depth, name="", position: Point = Point(0, 0), front_clearance=3, side_clearance=0, rear_clearance=0, orientation: Vector = Vector(0, 1), geometry_copy_equipment=None, offset_from_floor=0, clearance_above: bool = False):
        self.width = width
        self.height = height
        self.depth = depth
        self.name = name
        self.position = position
        self.offset_from_floor = offset_from_floor # Offset from the floor in feet
        self.clearance_above = clearance_above # Clearance above the equipment in feet
        # Add attributes for clearances
        self.front_clearance = front_clearance
        self.side_clearance = side_clearance
        self.rear_clearance = rear_clearance

        self.orientation = orientation

        self.clearance_geometry = self.create_rhino_geometry(clearance=True, equipment=False, geometry_copy_equipment=geometry_copy_equipment)
        self.equipment_geometry = self.create_rhino_geometry(equipment=True, clearance=False, geometry_copy_equipment=geometry_copy_equipment)
        self.geometry = self.create_rhino_geometry(equipment=True, clearance=True, geometry_copy_equipment=geometry_copy_equipment)

    def place(self):
        # Logic to place the equipment in the room
        pass

    def rotate(self, angle): # Rotate the equipment by a given angle in radians
        self.orientation = self.orientation.rotate(angle)
        # Update the geometry after rotation
        self.clearance_geometry = self.create_rhino_geometry(clearance=True, equipment=False)
        self.equipment_geometry = self.create_rhino_geometry(equipment=True, clearance=False)
        self.geometry = self.create_rhino_geometry(equipment=True, clearance=True)

    def orient(self, vector: Vector): # Orient the equipment to a given vector
        self.orientation = vector
        # Update the geometry after rotation
        self.clearance_geometry = self.create_rhino_geometry(clearance=True, equipment=False)
        self.equipment_geometry = self.create_rhino_geometry(equipment=True, clearance=False)
        self.geometry = self.create_rhino_geometry(equipment=True, clearance=True)

    def set_position(self, position: Point): # Set the position of the equipment
        old_position = self.position
        self.position = position
        # Update the geometry after rotation
        # self.clearance_geometry = self.create_rhino_geometry(clearance=True, equipment=False)
        # self.equipment_geometry = self.create_rhino_geometry(equipment=True, clearance=False)
        # self.geometry = self.create_rhino_geometry(equipment=True, clearance=True)        

        # Translate the geometry to the new position
        translation_vector = Rhino.Geometry.Vector3d(position.x - old_position.x, position.y - old_position.y, 0)
        
        for brep in self.equipment_geometry:
            brep.Translate(translation_vector)
        for brep in self.clearance_geometry:
            brep.Translate(translation_vector)
        for brep in self.geometry:
            brep.Translate(translation_vector)


    def create_rhino_geometry(self, equipment=True, clearance=True, geometry_copy_equipment=None) -> Rhino.Geometry.Brep:
        if geometry_copy_equipment:
            if equipment == True and clearance == True:
                return geometry_copy_equipment.geometry
            elif equipment == True and clearance == False:
                return geometry_copy_equipment.equipment_geometry
            elif equipment == False and clearance == True:
                return geometry_copy_equipment.clearance_geometry
            else: 
                return None

        else:
            if equipment: # If equipment is True, create the equipment geometry
                # Create a box geometry for the equipment
                # Width should be centered at the position
                min_x = self.position.x - self.width / 2 # min_x is the left side of the equipment
                max_x = self.position.x + self.width / 2 # max_x is the right side of the equipment
                min_y = self.position.y + self.rear_clearance # min_y is the rear side of the equipment (rear clearance is added)
                max_y = self.position.y + self.depth + self.rear_clearance # max_y is the front side of the equipment (depth + rear clearance)
                min_z = self.offset_from_floor # min_z is the bottom of the equipment
                max_z = self.height # max_z is the top of the equipment
                equipment_brep = Rhino.Geometry.Brep.CreateFromBox(
                    Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the equipment
            
            # Create clearance geometry
            if clearance:
                clearance_brep_list = [] # Initialize a list to store clearance geometry
                if self.front_clearance > 0: 
                    # Create a box geometry for the front clearance
                    # front_clearance should be along the positive y-axis and offset from the equipment

                    # front_clearance_width should be 30 inches or the width of the equipment
                    front_clearance_width = max(inches_to_feet(30), self.width) # front clearance width should be the maximum of front clearance and width of the equipment

                    # front_clearance_height should be the height of the equipment or 6.5 feet
                    front_clearance_height = max(6.5, self.height) # front clearance height should be the maximum of front clearance and height of the equipment

                    min_x = self.position.x - front_clearance_width / 2 # min_x is the left side of the equipment
                    max_x = self.position.x + front_clearance_width / 2 # max_x is the right side of the equipment
                    min_y = self.position.y + self.depth + self.rear_clearance # min_y is the front side of the equipment
                    max_y = self.position.y + self.depth + self.front_clearance + self.rear_clearance # max_y is the front side of the equipment + front clearance
                    min_z = 0 # min_z is the bottom of the equipment
                    max_z = front_clearance_height # max_z is the top of the equipment
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

                if self.clearance_above: # If clearance above is True
                    # Create a box geometry for the clearance above
                    # clearance_above should be along the positive z-axis and offset from the equipment above
                    min_x = self.position.x - self.width / 2 # min_x is the left side of the equipment
                    max_x = self.position.x + self.width / 2 # max_x is the right side of the equipment
                    min_y = self.position.y + self.rear_clearance # min_y is the rear side of the equipment (rear clearance is added)
                    max_y = self.position.y + self.depth + self.rear_clearance # max_y is the front side of the equipment (depth + rear clearance)
                    min_z = self.height # min_z is the top of the equipment
                    max_z = 10 # max_z is the top of the room
                    clearance_above_brep = Rhino.Geometry.Brep.CreateFromBox(
                        Rhino.Geometry.BoundingBox(min_x, min_y, min_z, max_x, max_y, max_z)) # Create a box geometry for the clearance above
                    clearance_brep_list.append(clearance_above_brep)

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
            
            if self.orientation.x == 1 and self.orientation.y == 0:
                # print('Orientation is 1, 0')
                rotation_angle = math.radians(-90)
            # print(f'Rotation angle: {rotation_angle}')

            if rotation_angle != 0:
                for brep in equipment_geometry:
                    brep.Rotate(rotation_angle, 
                                rotation_axis, self.position.to_gh_point())
            
            # Combine the geometry if there are multiple breps
            if len(equipment_geometry) > 1:
                result_breps = Rhino.Geometry.Brep.JoinBreps(equipment_geometry, 0.001)
                if result_breps:
                    equipment_geometry = []
                    for brep in result_breps:
                        equipment_geometry.append(brep)
                print(f'Created {len(equipment_geometry)} breps')

            # Return the combined geometry
            return equipment_geometry

# Define the Panelboard subclass
class Panelboard(ElectricalEquipment):
    
    def __init__(self, width=inches_to_feet(20), height=6, depth=inches_to_feet(5.75), name="",
                 position: Point = Point(0, 0), geometry_copy_equipment=None, offset_from_floor=inches_to_feet(30)):
        super().__init__(width, height, depth, name, position, 
                         geometry_copy_equipment=geometry_copy_equipment, 
                         offset_from_floor=offset_from_floor, clearance_above=True)
        # Additional attributes specific to panelboard
        # ...

# Define the Transformer subclass
class Transformer(ElectricalEquipment):
    def __init__(self, width=inches_to_feet(25.5), height=inches_to_feet(29.3), 
                 depth=inches_to_feet(25.9), name="",
                 position: Point = Point(0, 0), geometry_copy_equipment=None):
        self.rear_clearance = 0.25
        self.front_clearance = 3
        self.side_clearance = 0.25

        super().__init__(width, height, depth, name, position, 
                         self.front_clearance, self.side_clearance, 
                         self.rear_clearance, geometry_copy_equipment=geometry_copy_equipment)

# Define the ElectricalRoom class
class ElectricalRoom:
    # Initialize the electrical room with necessary attributes (e.g., dimensions, list of equipment)
    # ...
    def __init__(self, width, length, height=10):
        self.width = width
        self.length = length
        self.height = height
        self.equipment_list = []
        self.placed_equipment = []

        self.doors = []

        self.interior_rectangle = self.create_interior_rectangle()
        self.outline_geometry, self.difference_geometry = self.create_wall_geometry()

        self.south_wall_face = self.outline_geometry.Faces[9]
        self.north_wall_face = self.outline_geometry.Faces[7]
        self.east_wall_face = self.outline_geometry.Faces[8]
        self.west_wall_face = self.outline_geometry.Faces[6]
    
    # Method to add equipment to the room
    def add_equipment(self, equipment: ElectricalEquipment, count=1) -> bool:
        for i in range(count):
            self.equipment_list.append(equipment)
        return True
    
    def add_door_from_point(self, point: Point) -> bool:
        # Logic to add a door to the room
        # Return True if successful, False otherwise
        door = Door()
        self.doors.append(door)

        points, vectors = self.generate_points_and_vectors(flatten=False)

        door_width = door.width
        point_spacing = 0.5 # Spacing between points

        # Remove points that cannot fit the door, points that are too close to the corner
        number_of_points_to_remove_from_each_corner = door_width / 2 / point_spacing

        for edge_points, edge_vectors in zip(points, vectors):
            for i in range(int(number_of_points_to_remove_from_each_corner)):
                edge_points.pop(0)
                edge_points.pop(-1)
                edge_vectors.pop(0)
                edge_vectors.pop(-1)

        # Flatten the points and vectors
        points = [point for sublist in points for point in sublist]
        vectors = [vector for sublist in vectors for vector in sublist]

        # Get nearest point and vector to the door point
        nearest_point = None
        nearest_vector = None
        min_distance = float('inf')
        for p, v in zip(points, vectors):
            distance = p.distance(point)
            if distance < min_distance:
                min_distance = distance
                nearest_point = p
                nearest_vector = v

        print(f'Nearest point: {nearest_point.x}, {nearest_point.y}')
        
        # Set the position and orientation of the door
        door.set_position(nearest_point)
        door.orient(nearest_vector)

        # Update the wall geometry
        self.outline_geometry, self.difference_geometry = self.create_wall_geometry()
        self.south_wall_face = self.outline_geometry.Faces[9]
        self.north_wall_face = self.outline_geometry.Faces[7]
        self.east_wall_face = self.outline_geometry.Faces[8]
        self.west_wall_face = self.outline_geometry.Faces[6]

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
    def create_wall_geometry(self) -> tuple:
        wall_thickness = 0.5 # Thickness of the wall

        # Offset the interior rectangle to create the exterior rectangle
        interior_rectangle = self.interior_rectangle
        exterior_rectangle = self.create_exterior_rectangle(wall_thickness)

        edges = [interior_rectangle.ToNurbsCurve(), exterior_rectangle.ToNurbsCurve()]
        # Create a surface from both rectangles
        surface = Rhino.Geometry.Brep.CreatePlanarBreps(edges, 0.001)[0]

        # Extrude the surface to create the walls
        outline_brep = Rhino.Geometry.Brep.CreateFromOffsetFace(surface.Faces[0], self.height, 0.001, False, True)

        difference_brep = outline_brep
        # Cut the door from the wall
        for door in self.doors:
            void_brep = door.void
            difference_brep = list(Rhino.Geometry.Brep.CreateBooleanDifference(difference_brep, void_brep, 0.001))[0]
            
        return outline_brep, difference_brep
    
    # Method to generate points and vectors around the room
    def generate_points_and_vectors(self, flatten=True, spacing=0.5) -> tuple:
        # Create Points and Vectors around the room
        points = []
        vectors = []

        # Create points around the interior rectangle
        # spacing = 0.5 # Spacing between points
        interior_rectangle = self.interior_rectangle

        # Create points along the edges of the rectangle
        # It is important to note that the points are created in a clockwise direction
        # Starting from the bottom left corner

        # Create points along the bottom edge
        bottom_points = []
        bottom_vectors = []
        for i in range(int(interior_rectangle.Width / spacing) + 1):
            bottom_points.append(Point(interior_rectangle.Corner(0).X + i * spacing, interior_rectangle.Corner(0).Y))
            bottom_vectors.append(Vector(0, 1))
        # Create points along the top edge
        top_points = []
        top_vectors = []
        for i in range(int(interior_rectangle.Width / spacing)):
            top_points.append(Point(interior_rectangle.Corner(2).X - i * spacing, interior_rectangle.Corner(2).Y))
            top_vectors.append(Vector(0, -1))
        # Reverse the top points and vectors
        top_points.reverse()
        top_vectors.reverse()
        # Create points along the right edge
        right_points = []
        right_vectors = []
        for i in range(int(interior_rectangle.Height / spacing)):
            right_points.append(Point(interior_rectangle.Corner(1).X, interior_rectangle.Corner(1).Y + i * spacing))
            right_vectors.append(Vector(-1, 0))
        # Create points along the left edge
        left_points = []
        left_vectors = []
        for i in range(int(interior_rectangle.Height / spacing) + 1):
            left_points.append(Point(interior_rectangle.Corner(3).X, interior_rectangle.Corner(3).Y - i * spacing))
            left_vectors.append(Vector(1, 0))
        # Reverse the left points and vectors
        left_points.reverse()
        left_vectors.reverse()

        print(f'len(bottom_points): {len(bottom_points)}')
        print(f'len(top_points): {len(top_points)}')
        print(f'len(right_points): {len(right_points)}')
        print(f'len(left_points): {len(left_points)}')

        if flatten:
            points = bottom_points + top_points + right_points + left_points
            vectors = bottom_vectors + top_vectors + right_vectors + left_vectors
        else:
            points = [bottom_points, top_points, right_points, left_points]
            vectors = [bottom_vectors, top_vectors, right_vectors, left_vectors]

        return points, vectors
    
    def place_equipment(self, point, vector, equipment: ElectricalEquipment) -> bool:
        # Logic to place the equipment in the room
        # Return True if successful, False otherwise
        
        # Update the position of the equipment
        old_position = equipment.position
        equipment.set_position(point)
        old_vector = equipment.orientation
        equipment.orient(vector)

        def revert_position():
            equipment.set_position(old_position)
            equipment.orient(old_vector)

        # Check if equipment and clearance geometry intersect with the wall geometry
        # If they do, return False
        wall_intersection = False

        for e_geometry in equipment.geometry:
            intersection_result = Rhino.Geometry.Brep.CreateBooleanIntersection(self.difference_geometry, e_geometry, 0.001, False)
            if intersection_result:
                wall_intersection = True
                break
        if wall_intersection:
            print(f'Equipment {equipment.name} intersects with wall geometry at Point {point.x}, {point.y}')
            revert_position()
            return False
        else:
            print(f'Equipment {equipment.name} does not intersect with wall geometry')
        
        # Check if equipment and clearance geometry intersect with other equipment
        # If they do, return False
        for placed_equipment in self.placed_equipment:
            for placed_geometry in placed_equipment.equipment_geometry:
                for e_geometry in equipment.geometry:
                    intersection_result = Rhino.Geometry.Brep.CreateBooleanIntersection(placed_geometry, e_geometry, 0.001, False)
                    if intersection_result:
                        print(f'Equipment {equipment.name} intersects with other equipment at Point {point.x}, {point.y}')
                        revert_position()
                        return False
                    else:
                        print(f'Equipment {equipment.name} does not intersect with other equipment')

        # Check if equipment geometry intersects with other clearance geometry
        # If they do, return False
        for placed_equipment in self.placed_equipment + self.doors:
            for placed_geometry in placed_equipment.clearance_geometry:
                for e_geometry in equipment.equipment_geometry:
                    intersection_result = Rhino.Geometry.Brep.CreateBooleanIntersection(placed_geometry, e_geometry, 0.001, False)
                    if intersection_result:
                        print(f'Equipment {equipment.name} intersects with other clearance geometry at Point {point.x}, {point.y}')
                        revert_position()
                        return False
                    else:
                        print(f'Equipment {equipment.name} does not intersect with other clearance geometry')
        # If all checks pass, return True
        print(f'Equipment {equipment.name} placed successfully')
        return True

    # Method to layout the equipment in the room
    def layout_equipment(self, shuffle=False) -> bool:
        # Logic to layout the equipment in the room
        # Return True if successful, False otherwise
        # Create Points and Vectors around the room
        points, vectors = self.generate_points_and_vectors()

        equipment_list = self.equipment_list
        for equipment in equipment_list: print(equipment.name)
        if shuffle:
            equipment_list = random.sample(equipment_list, len(equipment_list)) # Shuffle the equipment list
            print('Equipment list shuffled')
        for equipment in equipment_list: print(equipment.name)
        # Place the equipment in the room one by one using the list of points and vectors
        for point, vector in zip(points, vectors):
            for equipment in equipment_list:
                if self.place_equipment(point, vector, equipment):
                    # If the equipment is placed successfully, add it to the placed equipment list
                    self.placed_equipment.append(equipment)
                    print(f'Equipment {equipment.name} placed at Point {point.x}, {point.y}')
                    equipment_list.remove(equipment)
                    break
        
        if len(equipment_list) == 0:
            print('All equipment placed successfully')
            return True
        else:
            print('Not all equipment placed successfully')
            return False
        
    def calculate_blocked_walls_distance(self) -> tuple:
        # Calculate the total distance of the walls
        total_wall_distance = self.width * 2 + self.length * 2
        for door in self.doors:
            total_wall_distance -= door.width

        # A wall is considered blocked if there is equipment within 3 feet of it
        # Create a points and vectors around the room
        points, vectors = self.generate_points_and_vectors(spacing=0.25)

        # Remove points and vectors that overlap with the door void
        for door in self.doors:
            door_void = door.void
            
            for point, vector in zip(points, vectors):
                # Offset the point by the vector * -0.25 to get the point inside the wall
                test_point = point.to_gh_point() + vector.to_gh_vector() * -0.25
                # Offset the point along the z-axis by 0.5 feet to get the point inside the wall
                test_point = Rhino.Geometry.Point3d(test_point.X, test_point.Y, test_point.Z + 0.5)
                intersection_result = door_void.IsPointInside(test_point, 0.001, True)
                # print(f'intersection_result: {intersection_result}')
                if intersection_result:
                    # print(f'Point {point.x}, {point.y} is inside door void')
                    points.remove(point)
                    vectors.remove(vector)
        
        # Create a list of points that are within 3 feet of the wall
        blocked_points = []
        offset = 2
        small_offset = 0.1
        total_offset = offset - small_offset
        for point, vector in zip(points, vectors):
            rhino_point = point.to_gh_point()
            # Offset the point along the vector by 0.1 feet
            rhino_point += vector.to_gh_vector() * small_offset
            rhino_vector = vector.to_gh_vector()
            # Create a line from the point away from the wall
            line = Rhino.Geometry.Line(rhino_point, rhino_point + rhino_vector * total_offset)
            
            # Check if the line intersects with equipment geometry or clearance geometry
            for equipment in self.placed_equipment:
                for geometry in equipment.geometry:
                    intersection_result = Rhino.Geometry.Intersect.Intersection.CurveBrep(line.ToNurbsCurve(), geometry, 0.001)
                    # print(f'intersection_result: {intersection_result[1]}')
                    # output.append(list(intersection_result[1]))
                    if len(list(intersection_result[1])) > 0:
                        output.append(line.ToNurbsCurve())
                        print(f'Point {point.x}, {point.y} is blocked by equipment {equipment.name}')
                        blocked_points.append(point)
                        break

        # Calculate the percentage of blocked points compared to the total number of points
        total_blocked_wall_distance = len(blocked_points) / len(points) * total_wall_distance

        return total_wall_distance, total_blocked_wall_distance

# OUTPUTS
equipment_geometry = []
clearance_geometry = []
all_equipment_geometry = []
room_geometry = []

output = []
messages = []

# Create an instance of ElectricalRoom
# INPUTS
# Dimensions of the room
room_width = float(room_width)
room_length = float(room_length)
room_height = 10
# door_count = 1
shuffle = True
electrical_room = ElectricalRoom(room_width, room_length,
                                    room_height)

# Create instances of Panelboard and Transformer
# INPUTS
panelboard_count = int(panelboard_count)
transformer_count = int(transformer_count)
shuffle = bool(shuffle)
door_point = Point(door_point.X, door_point.Y)

# Add the panelboard and transformer to the electrical room

example_panelboard = Panelboard(name='PBX')
for i in range(panelboard_count):
    p = Panelboard(name=f'PB{i+1}', geometry_copy_equipment=example_panelboard)
    electrical_room.add_equipment(p, 1)

example_transformer = Transformer(name='TX')
for i in range(transformer_count):
    t = Transformer(name=f'T{i+1}', geometry_copy_equipment=example_transformer)
    electrical_room.add_equipment(t, 1)

electrical_room.add_door_from_point(door_point)

# Layout the equipment in the room
layout_success = electrical_room.layout_equipment(shuffle=shuffle)
if layout_success:
    messages.append('Layout successful')
    messages.append(True)
else:
    messages.append('Layout failed')
    messages.append(False)

# Extract the geometry of the equipment and clearance
for equipment in electrical_room.placed_equipment:
    equipment_geometry.append(equipment.equipment_geometry)
    clearance_geometry.append(equipment.clearance_geometry)
    all_equipment_geometry.append(equipment.geometry)

room_geometry.append([electrical_room.difference_geometry])

for door in electrical_room.doors:
    room_geometry.append(door.door_geometry)
    
total_wall_distance, total_blocked_wall_distance = electrical_room.calculate_blocked_walls_distance()

print(f'Total wall distance: {total_wall_distance}')
print(f'Total blocked wall distance: {total_blocked_wall_distance}')
messages.append(total_wall_distance)
messages.append(total_blocked_wall_distance)

# Report equipment not placed
not_placed_counts = {}
if len(electrical_room.equipment_list) > 0:
    for equipment in electrical_room.equipment_list:
        equipment_found = False
        for placed_equipment in electrical_room.placed_equipment:
            if equipment.name == placed_equipment.name:
                print(f'Equipment {equipment.name} is in the placed equipment list')
                equipment_found = True
                break # If the equipment is in the placed equipment list, break
        if not equipment_found:
            print(f'Equipment {equipment.name} is not in the placed equipment list')
            # If the equipment is not in the placed equipment list, add it to the not placed counts
            class_name = equipment.__class__.__name__
            if class_name in not_placed_counts:
                not_placed_counts[class_name] += 1
            else:
                not_placed_counts[class_name] = 1

not_placed_messages = []
for key, value in not_placed_counts.items():
    if value > 1:
        not_placed_messages.append(f'{value} {key}s not placed')
    else:
        not_placed_messages.append(f'{value} {key} not placed')
if len(not_placed_messages) > 0:
    messages.append('\n'.join(not_placed_messages))
else:
    messages.append('All equipment placed successfully')

try:
    equipment_geometry = th.list_to_tree(equipment_geometry)
except:
    pass
try:
    clearance_geometry = th.list_to_tree(clearance_geometry)
except:
    pass
try:
    room_geometry = th.list_to_tree(room_geometry)
except:
    pass
print(f'output: {output}')
try:
    print(f'output to tree')
    output = th.list_to_tree(output)
except:
    pass