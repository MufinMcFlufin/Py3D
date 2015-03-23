import copy, sys, math, pygame
from operator import itemgetter

class Polygons():
    def __init__(self):
        self.point_list = []
        self.polygon_list = []
        self.rotate_list = []
        self.project_list = []
    
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
    
    def get_point(self, point_index):
        return self.point_list[point_index]
    
    def get_point_list(self, point_index_list):
        return [self.get_point(point_index) for point_index in point_index_list]
    
    def get_polygon(self, polygon_index):
        return self.polygon_list[polygon_index]
    
    def get_polygon_points(self, polygon_index):
        return self.polygon_list [polygon_index][0]
    
    def get_polygon_point_list(self, polygon_index):
        return [ self.get_point(point_index) for point_index in self.polygon_list [polygon_index][0] ]
    
    def rotate_point(self, point_index, angleX, angleY, angleZ):
        if self.rotate_list == []:
            self.rotate_list = copy.deepcopy(self.point_list)
        self.rotate_list [point_index] = self.point_list [point_index].rotateX(angleX).rotateY(angleY).rotateZ(angleZ)
    
    def rotate_points(self, point_list, angleX, angleY, angleZ):
        for point_index in point_list:
            self.rotate_point(point_index, angleX, angleY, angleZ)
    
    def rotate_polygon(self, polygon_index, angleX, angleY, angleZ):
        self.rotate_points(self.get_polygon_points(polygon_index), angleX, angleY, angleZ)
    
    def rotate_polygons(self, polygon_list, angleX, angleY, angleZ):
        for polygon_index in polygon_list:
            self.rotate_points(self.get_polygon_points(polygon_index), angleX, angleY, angleZ)
    
    def prj_point(self, point_index, screen_width, screen_height, fov, viewer_distance):
        if prj_list == []:
            self.project_list = copy.deepcopy(self.point_list)
        self.project_list [point_index] = self.rotate_list [point_index].project(screen_width(), screen_height(), fov, viewer_distance)
    
    def prj_points(self, point_list, screen_width, screen_height, fov, viewer_distance):
        for point_index in point_list:
            self.prj_point(point_index, screen_width, screen_height, fov, viewer_distance)
    
    def prj_all(self, screen_width, screen_height, fov, viewer_distance):
        self.project_list = [point.project(screen_width, screen_height, fov, viewer_distance) for point in self.rotate_list]
    
    def get_prj_point(self, point_index):
        return self.project_list [point_index] 
    
    def get_prj_points(self, point_list):
        return [ self.get_prj_point(point_index) for point_index in point_list]
    
    
    def get_prj_point_list(self, point_list):
        return [ self.get_prj_point(point_index) for point_index in point_list]
    
    def get_prj_polygon(self, polygon_index):
        return self.get_prj_points( self.get_polygon_points( polygon_index))
    
    def get_prj_polygons(self, polygon_list):
        return [ self.get_prj_polygon( polygon_index) for polygon_index in polygon_list]
    
    def get_2d_prj_point(self, point_index):
        return self.project_list [point_index].coords2d
    
    def get_2d_prj_points(self, point_list):
        return [ self.get_2d_prj_point(point_index) for point_index in point_list]
    
    def get_2d_prj_polygon(self, polygon_index):
        return self.get_2d_prj_points( self.get_polygon_points( polygon_index))
    
    def get_2d_prj_polygons(self, polygon_list):
        return [ self.get_2d_prj_polygon( polygon_index) for polygon_index in polygon_list]
    
    def get_prj_polygon_z(self, polygon_index):
        point_list = self.get_prj_polygon( polygon_index)
        return sum([ point.z for point in point_list]) / len( point_list)
    
    def get_prj_z_list(self):
        return [ (polygon_index, sum([ point.z for point in self.get_prj_point_list(point_list)]) / len( point_list)) for polygon_index, (point_list, color) in enumerate(self.polygon_list)]
    
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
        
        self.poly = Polygons()
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
        
        
        self.color_ref = {
        (255, 255, 255): 'white',
        (0, 255, 0): 'green',
        (255, 0, 0): 'red',
        (0, 0, 255): 'blue',
        (255, 102, 0): 'orange',
        (255, 255, 0): 'yellow',
        (0, 0, 0): 'black',
        (0, 32, 0): 'dark_green',
        }
        
        
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)
        self.orange = (255, 102, 0)
        self.yellow = (255, 255, 0)
        self.black = (0, 0, 0)
        self.dark_green = (0, 32, 0)
        
        self.point_color = self.green
        self.wire_color = self.white
        self.background_color = self.dark_green
        
        for line in open( "C:\\Users\\Joey\\Desktop\\Program Scripts\\Python\\Rubik's Programs\\point_data.txt" ):
            x, y, z = line.split()
            self.poly.add_point( Point3D( x, y, z))
        
        for line in open( "C:\\Users\\Joey\\Desktop\\Program Scripts\\Python\\Rubik's Programs\\polygon_data.txt" ):
            point_str, color_str = line.split('|')
            points = [ int(e) for e in point_str.split()]
            color = [ int(e) for e in color_str.split()]
            self.poly.add_polygon(points, color)
    
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
            
            self.poly.rotate_points( range(len(self.poly.point_list)), self.angleX, self.angleY, self.angleZ)
            self.poly.prj_all(self.screen.get_width(), self.screen.get_height(), self.fov, self.viewer_distance)
            
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

