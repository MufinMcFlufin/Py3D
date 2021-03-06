import copy, sys, math, pygame
from operator import itemgetter

mult = .01
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

master_color_ref = {
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
    def __init__(self, x, y, z, theta=0, phi=0, win_width=640, win_height=480):
        self.x, self.y, self.z = x, y, z
        self.theta, self.phi = theta, phi
        self.screen = Screen( win_width, win_height )
    
    def render(self, point_list):
        """ Returns 2d coordinates of applied perspective of point_list, 3rd coordinate of distance to camera for painterly algorithm. """
        # delta list is difference between x,y,z of points and camera
        self.delta_l = [ (
            point.x - self.x,
            point.y - self.y,
            point.z - self.z
            ) for point in point_list]
        # next, determines difference in angle between point and camera, and distance to camera
        self.theta_l = [ (
            math.atan2( float(x), float(z) ),
            math.atan2( float(y), float(z) ),
            math.sqrt( math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2))
            ) for x, y, z in self.delta_l ]
        # this is the angle from the camera's perspective that it would see the points, and distance to camera
        self.perspective_l = [ (
            theta - self.theta,
            self.phi - phi,
            dist
            ) for theta, phi, dist in self.theta_l ]
        # final calculations, to find the 2d coordinates of the perspective applied to the points, plus distance
        self.screen_l = [ (
            self.screen.win_width * self.screen.distance * math.tan( theta ) / self.screen.width + self.screen.win_width/2,
            self.screen.win_height * self.screen.distance * math.tan( phi ) / self.screen.height + self.screen.win_height/2,
            dist
            ) for theta, phi, dist in self.perspective_l ]
        return self.screen_l

class Screen():
    """ Screen class mostly meant to hold onto specific variables that only apply to the virtual screen that exists only in the mathematics of the render method. """
    def __init__(self, win_width, win_height, distance=2, rot=0, width=4/3.0, height=1):
        self.win_width, self.win_height = win_width, win_height
        self.distance = distance
        self.width, self.height = width, height

class Cubie():
    """ Individual cube pieces that collectively make up one cube. Contains local coordinates and location, along with it's own local color values. Meant to be a mobile object for the engine to use to manipulate faces. """
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
                self.polygons.add_polygon( (points - 4, points - 3, points - 1, points - 2), master_color_ref [color] )
            except KeyError:
                pass
    
    def rotate_x(self, rotate):
        return rotate_point_list( self.polygons.point_list, rotate )
    
    def rotate_y(self, rotate):
        return rotate_point_list( self.polygons.point_list, rotate )
    
    def rotate_z(self, rotate):
        return rotate_point_list( self.polygons.point_list, rotate )

class Polygons():
    """ Class dedicated to holding onto all information for all polygons. Stores information for actual polygons, points, colors, and management for everything between. """
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
    """ Class dedicated to have a single object for each point to contain it's x,y,z information. Will eventually add more, as needed. """
    def __init__(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)
    
    def rotate_x(self, angle):
        """ Rotates the point around the X axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y = self.y * cosa - self.z * sina
        z = self.y * sina + self.z * cosa
        return Point3D(self.x, y, z)
    
    def rotate_y(self, angle):
        """ Rotates the point around the Y axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z = self.z * cosa - self.x * sina
        x = self.z * sina + self.x * cosa
        return Point3D(x, self.y, z)
    
    def rotate_z(self, angle):
        """ Rotates the point around the Z axis by the given angle in degrees. """
        rad = angle * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x = self.x * cosa - self.y * sina
        y = self.x * sina + self.y * cosa
        return Point3D(x, y, self.z)
    
    def get_coords(self):
        return (self.x, self.y, self.z)
    
    coords = property(get_coords)

def rotate_point_list( point_list, rotate_x=0, rotate_y=0, rotate_z=0 ):
    return [ point.rotate_x( rotate_x ).rotate_y( rotate_y ).rotate_z( rotate_z ) for point in point_list ]

class Simulation:
    """ Main engine of the program. """
    def __init__(self, win_width = 640, win_height = 480):
        pygame.init()
        
        self.screen = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption("Simulation of a rotating 3D Cube")
        
        self.clock = pygame.time.Clock()
        
        self.cam = Camera( 0.0, 0.0, -10.0, win_width = win_width, win_height = win_height )
        
        self.rotate_x, self.rotate_y = 0, 0
        
        self.draw_points = True
        self.draw_wires = True
        self.draw_faces = False
        
        self.point_color = green
        self.wire_color = white
        self.background_color = dark_green
        
        #self.cube = Cubie(0,0,0,{'top':'white', 'front':'green', 'right':'red', 'back':'blue', 'left':'orange', 'bottom':'yellow'})
        
        self.poly = Polygons()
        
        for line in open( "point_data.txt" ):
            x, y, z = line.split()
            self.poly.add_point( Point3D( x, y, z))
        
        for line in open( "polygon_data.txt" ):
            point_str, color_str = line.split('|')
            points = [ int(e) for e in point_str.split()]
            color = [ int(e) for e in color_str.split()]
            self.poly.add_polygon(points, color)
    
    def run(self):
        """ Main Loop """
        point_i = 0
        d_y, d_x = 0, 0
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.draw_faces = not self.draw_faces
                    if event.key == pygame.K_2:
                        self.draw_wires = not self.draw_wires
                    if event.key == pygame.K_3:
                        self.draw_points = not self.draw_points
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        d_y, d_x = 0, 0
                        self.poly.point_list = rotate_point_list(
                            self.poly.point_list,
                            self.rotate_x,
                            self.rotate_y )
                        self.rotate_x, self.rotate_y = 0, 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.poly.point_list = rotate_point_list(
                            self.poly.point_list,
                            self.rotate_x,
                            self.rotate_y )
                        self.rotate_x, self.rotate_y = 0, 0
                if event.type == pygame.MOUSEMOTION:
                    if event.buttons == (0,0,1):
                        d_y, d_x = event.rel
            
            self.rotate_x -= d_x / 2.0
            self.rotate_y -= d_y / 2.0
            
            self.clock.tick(50)
            self.screen.fill( self.background_color )
            
            d_y *= 0.9
            d_x *= 0.9
            
            # Calculate the average Z values of each polygon.
            rendered_points = self.cam.render( rotate_point_list( self.poly.point_list, self.rotate_x, self.rotate_y ) )
            average_z = [ (
                point_list,
                color,
                sum( [rendered_points[point][2] for point in point_list] ) / len( point_list )
                ) for point_list, color in self.poly.polygon_list ]
            
            point_temp = self.poly.point_list[point_i]
            
            # print 'Point: %s\nCam: %s\nDelta: %s\nTheta: %s\nPerspective: %s\nScreen: %s\n' % (
            #     (point_temp.x, point_temp.y, point_temp.z),
            #     (self.cam.x, self.cam.y, self.cam.z, self.cam.theta, self.cam.phi),
            #     self.cam.delta_l[point_i],
            #     self.cam.theta_l[point_i],
            #     self.cam.perspective_l[point_i],
            #     self.cam.screen_l[point_i])
            
            # Draw the faces using the Painterly algorithm:
            # Distant faces are drawn before the closer ones, as determined by average distance of all points from camera
            for point_list, color, z_distance in sorted(average_z, key=itemgetter(2), reverse=True):
                point_coords = [ ( rendered_points[point][0], rendered_points[point][1] ) for point in point_list ]
                if self.draw_faces:
                    pygame.draw.polygon(self.screen, color, point_coords)
                if self.draw_wires:
                    pygame.draw.lines(self.screen, self.wire_color, True, point_coords)
                if self.draw_points:
                    for x,y in point_coords:
                        self.screen.fill( self.point_color, (x, y, 2, 2))
            
            self.screen.fill( red, ( rendered_points[point_i][0], rendered_points[point_i][1], 2, 2))
            pygame.display.flip()

if __name__ == "__main__":
    try:
        Simulation(win_width = 800, win_height = 600).run()
    except SystemExit:
        pass
    except:
        import time, traceback
        print '\n\n'
        traceback.print_exc()
        time.sleep(10000)

