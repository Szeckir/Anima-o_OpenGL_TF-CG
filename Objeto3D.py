from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *

"""
Classe Objeto3D
Esta classe é responsável por carregar um modelo 3D (.obj)
e armazenar seus vértices e faces. Ela não será mais responsável por desenhar
o objeto diretamente para a animação de partículas, mas sim por fornecer
os dados iniciais para o sistema de partículas.
"""
class Objeto3D:
        
    def __init__(self):
        self.vertices = [] # Lista de objetos Ponto para os vértices
        self.faces    = [] # Lista de listas de índices de vértices para as faces
        self.position = Ponto(0,0,0) # Posição do objeto (usado para o modelo, não para partículas individuais)
        self.rotation = (0,0,0,0) # Rotação do objeto (usado para o modelo, não para partículas individuais)
        pass

    def LoadFile(self, file:str):
        """
        Carrega um arquivo .obj e popula as listas de vértices e faces.
        :param file: Caminho para o arquivo .obj.
        """
        f = open(file, "r")

        # leitor de .obj baseado na descrição em https://en.wikipedia.org/wiki/Wavefront_.obj_file    
        for line in f:
            values = line.split(' ')
            # dividimos a linha por ' ' e usamos o primeiro elemento para saber que tipo de item temos

            if values[0] == 'v': 
                # item é um vértice, os outros elementos da linha são a posição dele
                self.vertices.append(Ponto(float(values[1]),
                                            float(values[2]),
                                            float(values[3])))

            if values[0] == 'f':
                # item é uma face, os outros elementos da linha são dados sobre os vértices dela
                self.faces.append([])
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    # dividimos cada elemento por '/'
                    self.faces[-1].append(int(fInfo[0]) - 1) # primeiro elemento é índice do vértice da face
                    # ignoramos textura e normal
                
            # ignoramos outros tipos de items, no exercício não é necessário e vai só complicar mais
        pass

    # As funções DesenhaVertices, DesenhaWireframe e Desenha não serão mais usadas
    # diretamente para a animação de partículas, mas podem ser mantidas para
    # depuração ou para desenhar o modelo completo em alguma fase.
    # Para o sistema de partículas, desenharemos as partículas individualmente.

    def DesenhaVertices(self):
        """
        Desenha os vértices do modelo. Útil para depuração.
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(.1, .1, .8)
        glPointSize(8)

        glBegin(GL_POINTS)
        for v in self.vertices:
            glVertex(v.x, v.y, v.z)
        glEnd()
        
        glPopMatrix()
        pass

    def DesenhaWireframe(self):
        """
        Desenha o modelo em modo wireframe. Útil para depuração.
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)         
        
        for f in self.faces:            
            glBegin(GL_LINE_LOOP)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass

    def Desenha(self):
        """
        Desenha o modelo preenchido. Útil para depuração ou para a fase inicial da animação.
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)         
        
        for f in self.faces:            
            glBegin(GL_TRIANGLE_FAN)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass
