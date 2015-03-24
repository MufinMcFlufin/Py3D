import copy, sys, math, pygame
from operator import itemgetter

cubie_size = 0.75
sticker_size = 0.5625
cubie_faces = [
    'top',
    'bottom',
    'front',
    'back',
    'right',
    'left',
]

white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
orange = (255, 102, 0)
yellow = (255, 255, 0)
black = (0, 0, 0)
dark_green = (0, 32, 0)

color_ref = {
(255, 255, 255): 'white',
(0, 255, 0): 'green',
(255, 0, 0): 'red',
(0, 0, 255): 'blue',
(255, 102, 0): 'orange',
(255, 255, 0): 'yellow',
(0, 0, 0): 'black',
(0, 32, 0): 'dark_green',
white: (255, 255, 255),
green: (0, 255, 0),
red: (255, 0, 0),
blue: (0, 0, 255),
orange: (255, 102, 0),
yellow: (255, 255, 0),
black: (0, 0, 0),
dark_green: (0, 32, 0),
}

class Camera():
    """ Camera class largely meant to handle converting points from real 3d coordinates to applied perspective, but also holds onto all related variables for data cleanliness, and for an easy way to manipulate the camera independent of other variables. """
    def __init__(self, x, y, z, theta=0, phi=0, width=640, height=320):
        self.x, self.y, self.z = x, y, z
        self.theta, self.phi = theta, phi
        self.screen = Screen( width, height )
    
    def render(self, point_list):
        """ Returns 2d coordinates of applied perspective of point_list, 3rd coordinate of distance to camera for painterly algorithm. """
        # delta list is difference between x,y,z of points and camera
        delta_l = [ (point.x - self.x, point.y - self.y, point.z - self.z) for point in point_list]
        # next, determines difference in angle between point and camera, and distance to camera
        delta_l = [ (math.atan(float(x)/float(z)), math.atan(float(y)/float(z)), math.sqrt( math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2))) for x, y, z in delta_l ]
        # this is the angle from the camera's perspective that it would see the points, and distance to camera
        perspective_l = [ (theta - self.theta, phi - self.phi, dist) for theta, phi, dist in delta_l ]
        # final calculations, to find the 2d coordinates of the perspective applied to the points, plus distance
        screen_l = [ (self.screen.distance * math.tan( theta ) + self.screen.width/2, self.screen.distance * math.tan( phi ) + self.screen.height/2, dist) for theta, phi, dist in perspective_l ]
        return screen_l

class Screen():
    """ Screen class mostly meant to hold onto specific variables that only apply to the virtual screen that exists only in the mathematics of the render method. """
    def __init__(self, width, height, distance=10, rot=0, theta=0, phi=0):
        self.width, self.height = width, height
        self.distance = distance
        self.rot, self.theta, self.phi = rot, theta, phi

class Cubie():
    def __init__(self, x, y, z, color_dict):
        self.polygons = Polygons()
        
        self.x, self.y, self.z = x, y, z
        self.theta, self.phi = 0, 0
        
        for corner_x in range(2):
            for corner_y in range(2):
                for corner_z in range(2):
                    self.polygons.add_point( Point3D(
                        corner_x * cubie_size/2 - cubie_size/2,
                        corner_y * cubie_size/2 - cubie_size/2,
                        corner_z * cubie_size/2 - cubie_size/2,
                        ))
        
        self.polygons.add_polygons([
            [(0,1,3,2),(black)],
            [(0,1,5,4),(black)],
            [(0,2,6,4),(black)],
            [(2,3,7,6),(black)],
            [(1,3,7,5),(black)],
            [(4,5,7,6),(black)],
        ])
        
        for face in cubie_faces:
            try:
                color = color_dict [face]
                # for loop through all possible faces, and check in color_dict
                # if returns result, color is added to list of points, and added as a polygon
                # this is the intended location to return a KeyError for the try/except
                if face == 'top':
                    for x in range(-1,2,2):
                        for z in range(-1,2,2):
                            self.polygons.add_point( Point3D( x*sticker_size/2, cubie_size/2 + 0.01, z*sticker_size/2 ))
                elif face == 'bottom':
                    for x in range(-1,2,2):
                        for z in range(-1,2,2):
                            self.polygons.add_point( Point3D( x*sticker_size/2, -cubie_size/2 - 0.01, z*sticker_size/2 ))
                elif face == 'front':
                    for x in range(-1,2,2):
                        for y in range(-1,2,2):
                            self.polygons.add_point( Point3D( x*sticker_size/2, y*sticker_size/2, cubie_size/2 + 0.01 ))
                elif face == 'back':
                    for x in range(-1,2,2):
                        for y in range(-1,2,2):
                            self.polygons.add_point( Point3D( x*sticker_size/2, y*sticker_size/2, -cubie_size/2 - 0.01 ))
                elif face == 'right':
                    for y in range(-1,2,2):
                        for z in range(-1,2,2):
                            self.polygons.add_point( Point3D( cubie_size/2 + 0.01, y*sticker_size/2, z*sticker_size/2 ))
                elif face == 'left':
                    for y in range(-1,2,2):
                        for z in range(-1,2,2):
                            self.polygons.add_point( Point3D( -cubie_size/2 - 0.01, y*sticker_size/2, z*sticker_size/2 ))
                points = len( self.polygons.point_list )
                self.polygons.add_polygon( (points - 4, points - 3, points - 1, points - 2), color_ref [color] )
            except KeyError:
                pass

class Polygons():
    def __init__(self):
        self.point_list = []
        self.polygon_list = []
    
    def add_point(self, point, check = False):
        if check:
            for check_point in self.point_list:
                if not point.get_coords == check_point.get_coords:
                    break
            else:
                self.point_list.append(point)
        else:
            self.point_list.append(point)
    
    def add_points(self, point_list, check = False):
        for point in point_list:
            self.add_point(point, check)
    
    def add_polygon(self, points, color, check = False):
        if check:
            for check_points, check_color in self.polygon_list:
                if points == check_points:
                    break
            else:
                self.polygon_list.append([points, color])
        else:
            self.polygon_list.append([points, color])
    
    def add_polygons(self, polygon_list, check = False):
        for points, color in polygon_list:
            self.add_polygon(points, color, check)
    
    def get_polygon_points(self, polygon_index):
        return self.polygon_list [polygon_index][0]
    
    def get_polygon_color(self, polygon_index):
        return self.polygon_list [polygon_index] [1]

class Point3D:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = float(x), float(y), float(z)
    
    def rotateX(self, angle):
        """ Rotates the point around the X axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y = self.y * cosa - self.z * sina
        z = self.y * sina + self.z * cosa
        return Point3D(self.x, y, z)
    
    def rotateY(self, angle):
        """ Rotates the point around the Y axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z = self.z * cosa - self.x * sina
        x = self.z * sina + self.x * cosa
        return Point3D(x, self.y, z)
    
    def rotateZ(self, angle):
        """ Rotates the point around the Z axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x = self.x * cosa - self.y * sina
        y = self.x * sina + self.y * cosa
        return Point3D(x, y, self.z)
    
    def project(self, win_width, win_height, fov, viewer_distance):
        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (viewer_distance + self.z)
        x = self.x * factor + win_width / 2
        y = -self.y * factor + win_height / 2
        return Point3D(x, y, self.z)
    
    def get_coords(self):
        return (self.x, self.y, self.z)
    
    def get_coords2d(self):
        return (self.x, self.y)
    
    coords = property(get_coords)
    coords2d = property(get_coords2d)

class Simulation:
    def __init__(self, win_width = 640, win_height = 480):
        pygame.init()
        
        self.screen = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption("Simulation of a rotating 3D Cube")
        
        self.clock = pygame.time.Clock()
        
        self.rotate = True
        self.angleX = 0
        self.angleY = 0
        self.angleZ = 0
        self.fov = 256
        self.viewer_distance = 4.0
        
        self.draw_points = False
        self.draw_wires = False
        self.draw_faces = True
        
        self.point_color = green
        self.wire_color = white
        self.background_color = dark_green
        
        self.cubes = [
            Cubie(0,0,0,{'top':'white'})
            ]
    
    def run(self):
        """ Main Loop """
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.draw_faces = not self.draw_faces
                    if event.key == pygame.K_p:
                        self.draw_points = not self.draw_points
                    if event.key == pygame.K_w:
                        self.draw_wires = not self.draw_wires
                    if event.key == pygame.K_KP9:
                        self.rotate = not self.rotate
                    if event.key == pygame.K_KP7:
                        self.angleX = 0
                        self.angleY = 0
                        self.angleZ = 0
                    if event.key == pygame.K_KP6:
                        self.angleZ += 10
                    if event.key == pygame.K_KP5:
                        self.angleY += 10
                    if event.key == pygame.K_KP4:
                        self.angleX += 10
                    if event.key == pygame.K_KP3:
                        self.angleZ -= 10
                    if event.key == pygame.K_KP2:
                        self.angleY -= 10
                    if event.key == pygame.K_KP1:
                        self.angleX -= 10
                    if event.key == pygame.K_o:
                        self.viewer_distance += .1
                    if event.key == pygame.K_l:
                        self.viewer_distance -= .1
                    if event.key == pygame.K_i:
                        self.fov += 8
                    if event.key == pygame.K_k:
                        self.fov -= 8
            
            self.clock.tick(50)
            self.screen.fill( self.background_color )
            
            # Calculate the average Z values of each face.
            average_z = self.poly.get_prj_z_list()
            # Draw the faces using the Painter's algorithm:
            # Distant faces are drawn before the closer ones.
            for poly_index, z_distance in sorted(average_z, key=itemgetter(1), reverse=True):
                pointlist = self.poly.get_2d_prj_polygon( poly_index)
                if self.draw_faces:
                    pygame.draw.polygon(self.screen, self.poly.get_polygon_color(poly_index), pointlist)
                if self.draw_wires:
                    pygame.draw.lines(self.screen, self.wire_color, True, pointlist)
                if self.draw_points:
                    for x,y in pointlist:
                        self.screen.fill( self.point_color, (x, y, 2, 2))
            if self.rotate:
                self.angleX += 1
                self.angleY += 1
                self.angleZ += 1
            
            pygame.display.flip()

if __name__ == "__main__":
    Simulation().run()
