import numpy as np
import math as mt

DEFCOLOR2D='#c1e328'
DEFCOLOR3D='#c1e328'

class Forme:
    def __init__(self, x:float=0, y:float=0, color:str=DEFCOLOR2D, type_:str='2D'):
        self.X = x
        self.Y = y
        self.color = color
        self.type = type_

    def formule(self):
        raise NotImplementedError

    def calculeAXE(self):
        raise NotImplementedError

class Forme2D(Forme):
    def Aire(self): raise NotImplementedError
    def Perimetre(self): raise NotImplementedError

class Forme3D(Forme):
    def __init__(self, x=0, y=0, z:float=0, color=DEFCOLOR3D):
        super().__init__(x, y, color=color, type_='3D')
        self.Z = z
    def Surface(self): raise NotImplementedError
    def Volume(self): raise NotImplementedError
# --- FORMES 2D ---

class Cercle(Forme2D):
    def __init__(self, x=0, y=0, r:float=1, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.r = r
    def Aire(self): return mt.pi * self.r**2
    def Perimetre(self): return 2 * mt.pi * self.r
    def formule(self): return {'Aire': r'A = \pi r^2', 'Périmètre': r'P = 2 \pi r'}
    def calculeAXE(self):
        t = np.linspace(0, 2*mt.pi, 100)
        X = self.X + self.r * np.cos(t)
        Y = self.Y + self.r * np.sin(t)
        return X, Y, np.zeros_like(X)

class Carre(Forme2D):
    def __init__(self, x=0, y=0, a:float=1, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.a = a
    def Aire(self): return self.a**2
    def Perimetre(self): return 4*self.a
    def formule(self): return {'Aire': r'A = a^2', 'Périmètre': r'P = 4a'}
    def calculeAXE(self):
        X = [self.X, self.X+self.a, self.X+self.a, self.X, self.X]
        Y = [self.Y, self.Y, self.Y+self.a, self.Y+self.a, self.Y]
        return np.array(X), np.array(Y), np.zeros(len(X))

class Rectangle(Forme2D):
    def __init__(self, x=0, y=0, l:float=2, w:float=1, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.l, self.w = l, w
    def Aire(self): return self.l * self.w
    def Perimetre(self): return 2*(self.l + self.w)
    def formule(self): return {'Aire': r'A = l \cdot w', 'Perimetre': r'P = 2(l + w)'}
    def calculeAXE(self):
        X = [self.X, self.X+self.l, self.X+self.l, self.X, self.X]
        Y = [self.Y, self.Y, self.Y+self.w, self.Y+self.w, self.Y]
        return np.array(X), np.array(Y), np.zeros(len(X))

class TriangleEquilateral(Forme2D):
    def __init__(self, x=0, y=0, a:float=1, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.a = a
    def Aire(self): return mt.sqrt(3)/4 * self.a**2
    def Perimetre(self): return 3*self.a
    def formule(self): return {'Aire': r'A = \frac{\sqrt{3}}{4} a^2', 'Perimetre': r'P = 3a'}
    def calculeAXE(self):
        h = mt.sqrt(3)/2 * self.a
        X = [self.X, self.X+self.a, self.X+self.a/2, self.X]
        Y = [self.Y, self.Y, self.Y+h, self.Y]
        return np.array(X), np.array(Y), np.zeros(len(X))

class Ellipse(Forme2D):
    def __init__(self, x=0, y=0, a:float=2, b:float=1, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.a, self.b = a, b
    def Aire(self): return mt.pi * self.a * self.b
    def Perimetre(self): return mt.pi * (3*(self.a + self.b) - mt.sqrt((3*self.a + self.b)*(self.a + 3*self.b)))
    def formule(self): return {'Aire': r'A = \pi a b', 'Perimetre': r'P \approx \text{Ramanujan approx}'}
    def calculeAXE(self):
        t = np.linspace(0, 2*mt.pi, 100)
        X = self.X + self.a * np.cos(t)
        Y = self.Y + self.b * np.sin(t)
        return X, Y, np.zeros_like(X)

class Polygone(Forme2D):
    def __init__(self, x=0, y=0, n:int=5, r:float=2, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.n, self.r = n, r
    def Aire(self): return (self.n * self.r**2 * mt.sin(2*mt.pi/self.n)) / 2
    def Perimetre(self): return 2 * self.n * self.r * mt.sin(mt.pi / self.n)
    def formule(self): return {'Aire': r'A = \frac{n r^2 \sin(2\pi/n)}{2}', 'Périmètre': r'P = 2nr \sin(\pi/n)'}
    def calculeAXE(self):
        angles = np.linspace(0, 2*mt.pi, self.n+1)
        X = self.X + self.r * np.cos(angles)
        Y = self.Y + self.r * np.sin(angles)
        return X, Y, np.zeros_like(X)

class Losange(Forme2D):
    def __init__(self, x=0, y=0, D=4, d=2, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.D, self.d = D, d
    def Aire(self): return (self.D * self.d) / 2
    def Perimetre(self): return 4 * mt.sqrt((self.D/2)**2 + (self.d/2)**2)
    def formule(self): return {'Aire': r'A = \frac{D \cdot d}{2}', 'Périmètre': r'P = 4 \sqrt{(D/2)^2 + (d/2)^2}'}
    def calculeAXE(self):
        X = np.array([0, self.D/2, 0, -self.D/2, 0]) + self.X
        Y = np.array([self.d/2, 0, -self.d/2, 0, self.d/2]) + self.Y
        return X, Y, np.zeros_like(X)

class SecteurCirculaire(Forme2D):
    def __init__(self, x=0, y=0, r=2, angle_deg=120, color=DEFCOLOR2D):
        super().__init__(x, y, color)
        self.r, self.angle_deg = r, angle_deg
    def Aire(self): return (mt.pi * self.r**2) * (self.angle_deg / 360)
    def Perimetre(self): return (2 * mt.pi * self.r * self.angle_deg / 360) + 2 * self.r
    def formule(self): return {'Aire': r'A = \frac{\theta}{360} \pi r^2', 'Périmètre': r'P = L + 2r'}
    def calculeAXE(self):
        theta = np.linspace(0, np.radians(self.angle_deg), 50)
        x_arc = self.r * np.cos(theta)
        y_arc = self.r * np.sin(theta)
        X = np.concatenate(([0], x_arc, [0])) + self.X
        Y = np.concatenate(([0], y_arc, [0])) + self.Y
        return X, Y, np.zeros_like(X)

# --- FORMES 3D ---

class Cube(Forme3D):
    def __init__(self, a:float=1, color=DEFCOLOR3D):
        super().__init__(0, 0, 0, color)
        self.a = a
    def formule(self): return {'Surface': r'S = 6a^2', 'Volume': r'V = a^3'}
    def Surface(self): return 6 * self.a**2
    def Volume(self): return self.a**3
    def calculeAXE(self):
        a = self.a
        # Points pour fil de fer (Wireframe)
        pts = [[0,0,0], [a,0,0], [a,a,0], [0,a,0], [0,0,0], 
               [0,0,a], [a,0,a], [a,a,a], [0,a,a], [0,0,a], 
               [0,a,a], [0,a,0], [a,a,0], [a,a,a], [a,0,a], [a,0,0]]
        Matric = np.array(pts).T
        return Matric[0], Matric[1], Matric[2]

class Sphere(Forme3D):
    def __init__(self, r:float=1, color=DEFCOLOR3D):
        super().__init__(0, 0, 0, color)
        self.r = r
    def formule(self): return {'Surface': r'S = 4\pi r^2', 'Volume': r'V = \frac{4}{3}\pi r^3'}
    def Surface(self): return 4 * mt.pi * self.r**2
    def Volume(self): return 4/3 * mt.pi * self.r**3
    def Circonscription(self): return 2*mt.pi*self.r # CORRIGÉ ICI
    def Diametre(self): return self.r*2
    def calculeAXE(self):
        u = np.linspace(0, mt.pi, 30)
        v = np.linspace(0, 2*mt.pi, 30)
        u, v = np.meshgrid(u, v)
        x = self.r * np.sin(u) * np.cos(v)
        y = self.r * np.sin(u) * np.sin(v)
        z = self.r * np.cos(u)
        return x, y, z

class Cylindre(Forme3D):
    def __init__(self, r:float=1, h:float=2, color=DEFCOLOR3D):
        super().__init__(0, 0, 0, color)
        self.r, self.h = r, h
    def formule(self): return {'Surface_T': r'S_T = 2\pi r(r + h)', 'Volume': r'V = \pi r^2 h'}
    def Surface(self):
        AB = mt.pi*self.r**2
        SL = 2*mt.pi*self.r*self.h
        ST = 2*mt.pi*self.r*(self.r + self.h)
        return AB, SL, ST
    def Volume(self): return mt.pi*self.r**2*self.h
    def calculeAXE(self):
        t = np.linspace(0, 2*mt.pi, 50)
        z = np.linspace(0, self.h, 2)
        t, z = np.meshgrid(t, z)
        x = self.r * np.cos(t)
        y = self.r * np.sin(t)
        return x, y, z

class Cone(Forme3D):
    def __init__(self, r:float=1, h:float=2, color=DEFCOLOR3D):
        super().__init__(0, 0, 0, color)
        self.r, self.h = r, h
    def formule(self): return {'Surface_T': r'S = \pi r (r + s)', 'Volume': r'V = \frac{1}{3} \pi r^2 h'}
    def Surface(self):
        s = mt.sqrt(self.r**2 + self.h**2)
        SL = mt.pi*self.r*s
        ST = mt.pi*self.r*(self.r+s)
        return s, SL, ST
    def Volume(self): return (1/3) * mt.pi * self.h * self.r**2
    def calculeAXE(self):
        t = np.linspace(0, 2*mt.pi, 50)
        z = np.linspace(0, self.h, 50)
        t, z = np.meshgrid(t, z)
        x = self.r * (1 - z/self.h) * np.cos(t)
        y = self.r * (1 - z/self.h) * np.sin(t)
        return x, y, z

class PyramideCarree(Forme3D):
    def __init__(self, a=2, h=3, color=DEFCOLOR3D):
        super().__init__(0, 0, 0, color)
        self.a, self.h = a, h
    def formule(self): return {'Surface': r'S = a^2 + 2a\sqrt{a^2 + h^2}', 'Volume': r'V = \frac{1}{3} a^2 h'}
    def Surface(self):
        s = mt.sqrt((self.a/2)**2 + self.h**2)
        SL = 2*self.a*s
        ST = self.a**2 + SL
        return s, SL, ST 
    def Volume(self): return (1/3) * self.a**2 * self.h
    def calculeAXE(self):
        a, h = self.a, self.h
        X = [0, a, a, 0, a/2, 0, 0, a, a/2, a]
        Y = [0, 0, a, a, a/2, 0, a, a, a/2, 0]
        Z = [0, 0, 0, 0, h, 0, 0, 0, h, 0]
        return np.array(X), np.array(Y), np.array(Z)

class Tore(Forme3D):
    def __init__(self, R=3, r=1, color=DEFCOLOR3D):
        super().__init__(0, 0, 0, color)
        self.R, self.r = R, r
    def Surface(self): return 4 * mt.pi**2 * self.R * self.r
    def Volume(self): return 2 * mt.pi**2 * self.R * self.r**2
    def formule(self): return {'Surface': r'S = 4\pi^2 R r', 'Volume': r'V = 2\pi^2 R r^2'}
    def calculeAXE(self):
        u = np.linspace(0, 2*mt.pi, 40)
        v = np.linspace(0, 2*mt.pi, 40)
        U, V = np.meshgrid(u, v)
        X = (self.R + self.r * np.cos(V)) * np.cos(U)
        Y = (self.R + self.r * np.cos(V)) * np.sin(U)
        Z = self.r * np.sin(V)
        return X, Y, Z