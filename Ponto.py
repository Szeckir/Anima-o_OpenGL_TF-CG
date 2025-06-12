import math

""" Classe Ponto """
class Ponto: 
    def __init__(self, x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    
    """ Imprime os valores de cada eixo do ponto """
    # Faz a impressao usando sobrecarga de funcao
    # https://www.educative.io/edpresso/what-is-method-overloading-in-python
    def imprime(self, msg=None):
        if msg is not None:
            print (msg, self.x, self.y, self.z)
        else:
            print (self.x, self.y, self.z)

    """ Define os valores dos eixos do ponto """
    def set(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
    
# Definicao de operadores
# https://www.programiz.com/python-programming/operator-overloading
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z # Adicionado z para operações 3D
        return Ponto(x, y, z)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z # Adicionado z para operações 3D
        return Ponto(x, y, z)

    def __mul__(self, scalar: float): # Renomeado 'other' para 'scalar' e tipo para float
        x = self.x * scalar
        y = self.y * scalar
        z = self.z * scalar # Adicionado z para operações 3D
        return Ponto(x, y, z)

    def __truediv__(self, scalar: float): # Adicionado para divisão por escalar
        if scalar == 0:
            raise ValueError("Não é possível dividir por zero.")
        x = self.x / scalar
        y = self.y / scalar
        z = self.z / scalar
        return Ponto(x, y, z)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        l = self.length()
        if l == 0:
            return Ponto(0,0,0)
        return self / l

    def copy(self):
        return Ponto(self.x, self.y, self.z)

    def rotacionaZ(self, angulo):
        anguloRad = angulo * math.pi/180.0
        xr = self.x*math.cos(anguloRad) - self.y*math.sin(anguloRad)
        yr = self.x*math.sin(anguloRad) + self.y*math.cos(anguloRad)
        self.x = xr
        self.y = yr

    def rotacionaY(self, angulo):
        anguloRad = angulo* math.pi/180.0
        xr =  self.x*math.cos(anguloRad) + self.z*math.sin(anguloRad)
        zr = -self.x*math.sin(anguloRad) + self.z*math.cos(anguloRad)
        self.x = xr
        self.z = zr
    
    def rotacionaX(self, angulo):
        anguloRad = angulo* math.pi/180.0
        yr =  self.y*math.cos(anguloRad) - self.z*math.sin(anguloRad)
        zr =  self.y*math.sin(anguloRad) + self.z*math.cos(anguloRad)
        self.y = yr
        self.z = zr

# ********************************************************************** */
#                                                                         */
# Calcula a interseccao entre 2 retas (no plano "XY" Z = 0)              */
#                                                                         */
# k : ponto inicial da reta 1                                             */
# l : ponto final da reta 1                                               */
# m : ponto inicial da reta 2                                             */
# n : ponto final da reta 2                                               */
# 
# Retorna:
# 0, se não houver interseccao ou 1, caso haja                            */
# int, valor do parâmetro no ponto de interseção (sobre a reta KL)        */
# int, valor do parâmetro no ponto de interseção (sobre a reta MN)        */
#                                                                         */
# ********************************************************************** */
def intersec2d(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> (int, float, float):
    det = (n.x - m.x) * (l.y - k.y)  -  (n.y - m.y) * (l.x - k.x)

    if (det == 0.0):
        return 0, None, None # não há intersecção

    s = ((n.x - m.x) * (m.y - k.y) - (n.y - m.y) * (m.x - k.x))/ det
    t = ((l.x - k.x) * (m.y - k.y) - (l.y - k.y) * (m.x - k.x))/ det

    return 1, s, t # há intersecção

# **********************************************************************
# HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto)
# Detecta interseccao entre os pontos
#
# **********************************************************************
def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> bool:
    ret, s, t = intersec2d( k,  l,  m,  n)

    if not ret: return False

    return s>=0.0 and s <=1.0 and t>=0.0 and t<=1.0
