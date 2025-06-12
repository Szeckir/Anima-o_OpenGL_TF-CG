from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import time
import math

from Objeto3D import Objeto3D
from Particle import Particle
from Ponto import Ponto

 # 0: parada, 1: Nodding, 2: desmonta, 3: furacao, 4:forma, 5: extra
head_model: Objeto3D
particles = []
animation_time = 0.0 #calcular tempo total
hora_ultimo_frame = 0.0  #seg ultimo frame
animation_speed = 1.0
is_playing = False
animation_phase = 0

# tempos
TEMPO_CABECA_DIZENDO_SIM = 1.5 
TEMPO_CABECA_CAINDO = 5.0
TEMPO_ESPERA_NO_CHAO = 2.0
TEMPO_TORNADO_REFORMANDO = 7.0
TEMPO_CABECA_FORMADA = 2.0
TEMPO_EFEITO_PULSAR = 10.0
TEMPO_TOTAL_ANIMACAO = TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA + TEMPO_EFEITO_PULSAR

# forças
FORCA_GRAVIDADE = Ponto(0, -9.8, 0) #cai
QUICAR = 0.6 #sobe

# camera
camera_zoom = 1.0; 
controlar_cam = False;

current_camera_target = Ponto(0, 0, 0) 
current_camera_position = Ponto(-2, 6, -8)

#posicao cam p/ etapas transição
camera_config = {
    "initial": {"pos": Ponto(-2, 6, -8), "target": Ponto(0, 0, 0)},
    "falling": {"pos_offset_y": 1.5, "pos_offset_z": -5.0, "pos_offset_x": -1.0, "target_offset_y": 0.0},
    "tornado": {"pos": Ponto(0, -2, 5), "target": Ponto(0, 0, 0)}, # Posição inicial do tornado
    "final": {"pos": Ponto(5, 2, 0), "target": Ponto(0, 0, 0)}, # Posição final da câmera (lateral)
    "extra": {"pos": Ponto(0, 3, 8), "target": Ponto(0, 0, 0)} # Nova posição para ver a cabeça de frente
}

def init(): 
    global head_model, particles, hora_ultimo_frame, current_camera_position, current_camera_target
    
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS) 
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 

    head_model = Objeto3D()
    head_model.LoadFile('Human_Head.obj')

    for vertex in head_model.vertices:
        particles.append(Particle(vertex))

    current_camera_position = camera_config["initial"]["pos"].copy()
    current_camera_target = camera_config["initial"]["target"].copy()

    DefineLuz()
    PosicUser()

    hora_ultimo_frame = time.time() # Inicializa o tempo do último frame

def DefineLuz(): # codigo base
    luz_ambiente = [0.4, 0.4, 0.4, 1.0]
    luz_difusa = [0.7, 0.7, 0.7, 1.0]
    luz_especular = [0.9, 0.9, 0.9, 1.0]
    posicao_luz = [2.0, 3.0, 0.0, 1.0]  # Posição da Luz
    especularidade = [1.0, 1.0, 1.0, 1.0]

    glEnable(GL_COLOR_MATERIAL)

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)

    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)

    glEnable(GL_COLOR_MATERIAL)

    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)

    glMateriali(GL_FRONT, GL_SHININESS, 51)

def PosicUser(): # codigo base
    global current_camera_target, current_camera_position, animation_time, TEMPO_CABECA_DIZENDO_SIM, TEMPO_CABECA_CAINDO, TEMPO_ESPERA_NO_CHAO, TEMPO_TORNADO_REFORMANDO, controlar_cam, camera_zoom

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()    

    gluPerspective(60, 4/4, 0.01, 50) 
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # ia ajudou para suavizar movimento da camera
    cam_interpolacao = 0.08 

    if animation_time < TEMPO_CABECA_DIZENDO_SIM:
        target_pos = camera_config["initial"]["pos"]
        target_target = camera_config["initial"]["target"]
    
    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO:
        # calcula ponto central
        avg_x = sum(p.current_pos.x for p in particles) / len(particles)
        avg_y = sum(p.current_pos.y for p in particles) / len(particles)
        avg_z = sum(p.current_pos.z for p in particles) / len(particles)
        
        target_target = Ponto(avg_x, avg_y, avg_z)  
        target_pos = Ponto( avg_x - 1.0, avg_y + 1.5, avg_z - 5.0)

    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO:
        tempo_atual_fase = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO)
        progresso = tempo_atual_fase / TEMPO_TORNADO_REFORMANDO
        
        CAMERA_INICIAL_Y = -2.0  # Posição Y inicial (embaixo)
        CAMERA_FINAL_Y = 3.0     # Posição Y final (em cima)
        
        ALVO_INICIAL_Y = 0.0     # Altura inicial do ponto para onde a câmera olha
        ALVO_FINAL_Y = 3.0       # Altura final do ponto para onde a câmera olha
        
        altura_camera = CAMERA_INICIAL_Y + (CAMERA_FINAL_Y - CAMERA_INICIAL_Y) * progresso
        altura_alvo = ALVO_INICIAL_Y + (ALVO_FINAL_Y - ALVO_INICIAL_Y) * progresso
        
        target_pos = Ponto(0, altura_camera, 5)  # Fixo em X e Z, sobe em Y
        target_target = Ponto(0, altura_alvo, 0) # Olha para o centro, subindo em Y

    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA:
        target_pos = Ponto(
            camera_config["final"]["pos"].x,
            camera_config["final"]["pos"].y,
            camera_config["final"]["pos"].z
        )
        target_target = Ponto(
            camera_config["final"]["target"].x,
            camera_config["final"]["target"].y,
            camera_config["final"]["target"].z
        )
        
    else:        
        target_pos = camera_config["extra"]["pos"]
        target_target = camera_config["extra"]["target"]
        
        cam_interpolacao = 0.08

    if animation_time >= TEMPO_TOTAL_ANIMACAO:
        controlar_cam = True

    if controlar_cam == True:
        direction = Ponto(
            current_camera_position.x - current_camera_target.x,
            current_camera_position.y - current_camera_target.y, 
            current_camera_position.z - current_camera_target.z
        )
        
        # Normaliza a direção
        direction_length = direction.length()
        if direction_length > 0:
            direction = direction / direction_length
            
        # Posição ajustada com base no zoom
        current_camera_position = Ponto(
            current_camera_target.x + direction.x * camera_zoom,
            current_camera_target.y + direction.y * camera_zoom,
            current_camera_target.z + direction.z * camera_zoom
        )

    if not controlar_cam:  
        current_camera_position = mover_camera_suave(current_camera_position, target_pos, cam_interpolacao)
        current_camera_target = mover_camera_suave(current_camera_target, target_target, cam_interpolacao)

    # if not controlar_cam:
    #     current_camera_position = target_pos.copy()
    #     current_camera_target = target_target.copy()

    gluLookAt(current_camera_position.x, current_camera_position.y, current_camera_position.z,
            current_camera_target.x, current_camera_target.y, current_camera_target.z,
            0, 1.0, 0)

#codigo base
def DesenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)  # desenha QUAD preenchido
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)  # desenha a borda da QUAD
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

#codigo base
def DesenhaPiso():
    glPushMatrix()
    glTranslated(-20, -1, -10) # Ajusta a posição do piso
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            DesenhaLadrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

# desenha cada vertice da fase
def desenha():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)

    PosicUser()
    DesenhaPiso()

    global animation_time, TEMPO_CABECA_DIZENDO_SIM, TEMPO_CABECA_CAINDO, TEMPO_ESPERA_NO_CHAO, TEMPO_TORNADO_REFORMANDO

    if animation_time < TEMPO_CABECA_DIZENDO_SIM:
        qtd_movimentos_cabeca = 2
        angulo_max = 30.0

        fase = animation_time / TEMPO_CABECA_DIZENDO_SIM * (qtd_movimentos_cabeca * 2 * math.pi)
        angle = angulo_max * (1 + math.sin(fase)) / 2
        
        glPushMatrix() # salva atual
        glRotatef(angle, 1, 0, 0) 
        head_model.DesenhaWireframe() 
        glPopMatrix() # restaura anterior

    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO:
        glPointSize(5) # tam vertices
        glBegin(GL_POINTS)
        for p in particles:
            glVertex3f(p.current_pos.x, p.current_pos.y, p.current_pos.z)
        glEnd()
    
    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO:
        glPointSize(5) 
        glBegin(GL_POINTS)
        for p in particles:
            glVertex3f(p.current_pos.x, p.current_pos.y, p.current_pos.z)
        glEnd();
    
    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA:
        glPointSize(5);
        glBegin(GL_POINTS)
        for p in particles:
            glVertex3f(p.current_pos.x, p.current_pos.y, p.current_pos.z)
        glEnd();
    
    else:
        glPointSize(5)
        current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA)
        angle = current_phase_time * 36 
        
        glPushMatrix()
        glRotatef(angle, 0, 1, 0) 
        glBegin(GL_POINTS)

        for p in particles:
            glColor3fv(p.color)
            glVertex3f(p.current_pos.x, p.current_pos.y, p.current_pos.z)
        glEnd()
        
        glPopMatrix()

    glutSwapBuffers()

def mover_camera_suave(atual, alvo, velocidade):
    return Ponto(
        atual.x + (alvo.x - atual.x) * velocidade,
        atual.y + (alvo.y - atual.y) * velocidade,
        atual.z + (alvo.z - atual.z) * velocidade
    )

# fica sendo chamada a cada frame
def update_animation():
    global animation_time, hora_ultimo_frame, animation_phase, is_playing

    hora_atual = time.time()
    dt = hora_atual - hora_ultimo_frame
    hora_ultimo_frame = hora_atual

    if is_playing:
        animation_time += dt * animation_speed 

        if animation_time < TEMPO_CABECA_DIZENDO_SIM:
            pass 

        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO:
            ALTURA_CHAO = -1.0
            ATRITO = 0.95
            
            for p in particles:
                p.apply_force(FORCA_GRAVIDADE)
                p.update(dt)
                
                if p.current_pos.y < ALTURA_CHAO:
                    p.current_pos.y = ALTURA_CHAO
                    p.velocity.y = -p.velocity.y * QUICAR
                    
                    if abs(p.velocity.y) < 0.1:
                        p.velocity.y = 0
                        
                    p.velocity.x *= ATRITO
                    p.velocity.z *= ATRITO
        
        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO:
            for p in particles:
                p.velocity = Ponto(0,0,0)
                p.acceleration = Ponto(0,0,0)
            pass

        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO:
            current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO)
            progress = current_phase_time / TEMPO_TORNADO_REFORMANDO
            
            redemoinho_centro = Ponto(0, -1.0 + 5.0 * progress, 0)

            for p in particles:
                direction = (redemoinho_centro - p.current_pos).normalize()
                dir_red = Ponto(-direction.z, 0, direction.x).normalize()

                forca_atracao = direction * 6.0
                forca_redemoinho = dir_red * 3.0
                forca_cima = Ponto(0, 3.0 * progress, 0)

                forca_total = forca_atracao + forca_redemoinho + forca_cima
                p.apply_force(forca_total)
                p.update(dt)

                if (p.current_pos - p.original_pos).length() < 0.1:
                    p.reset_position()

        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA:
            for p in particles:
                p.current_pos = p.original_pos.copy()
                p.velocity = Ponto(0,0,0)
                p.acceleration = Ponto(0,0,0)
        else:
            tempo_total = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA)
            pulsacao = 1 + 0.05 * math.sin(tempo_total * 2 * math.pi)
            ciclo = tempo_total / 2.0

            for p in particles:
                p.current_pos = p.original_pos * pulsacao
                r = 0.5 + 0.5 * math.sin(ciclo * 2 * math.pi)
                g = 0.5 + 0.5 * math.sin(ciclo * 2 * math.pi + 2 * math.pi/3)
                b = 0.5 + 0.5 * math.sin(ciclo * 2 * math.pi + 4 * math.pi/3)
                p.color = [r, g, b]
                p.velocity = Ponto(0,0,0)
                p.acceleration = Ponto(0,0,0)

        if animation_time > TEMPO_TOTAL_ANIMACAO:
            animation_time = TEMPO_TOTAL_ANIMACAO
            is_playing = False 

    glutPostRedisplay() 

def teclado(key, x, y):
    global is_playing, animation_time, animation_speed, animation_phase, particles, current_camera_position, current_camera_target, camera_zoom, controlar_cam

    key = key.decode("utf-8").upper() 

    if key == 'P': 
        is_playing = not is_playing
        print("play" if is_playing else "pausada")
    elif key == 'R':
        animation_time = 0.0 
        for p in particles:
            p.reset_position()
        current_camera_position = camera_config["initial"]["pos"].copy()
        current_camera_target = camera_config["initial"]["target"].copy()
        print("reiniciada")
    elif key == 'F': 
        animation_time = TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO
        for p in particles: 
            p.reset_position()
        current_camera_position = camera_config["final"]["pos"].copy()
        current_camera_target = camera_config["final"]["target"].copy()
        print("animacao avancada")
    elif key == 'W':  
        if animation_time >= TEMPO_TOTAL_ANIMACAO:  
            camera_zoom -= 0.5 
            camera_zoom = max(2.0, camera_zoom)  
    elif key == 'S': 
        if animation_time >= TEMPO_TOTAL_ANIMACAO:  
            camera_zoom += 0.5  
            camera_zoom = min(20.0, camera_zoom) 

    glutPostRedisplay()

# codigo base
def main():
    glutInit(sys.argv)

    # Define o modelo de operacao da GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE) # Adicionado GLUT_DOUBLE para double buffering

    # Especifica o tamanho inicial em pixels da janela GLUT (400x400 conforme requisito)
    glutInitWindowSize(400, 400)

    # Especifica a posição de início da janela
    glutInitWindowPosition(100, 100)

    # Cria a janela passando o título da mesma como argumento
    glutCreateWindow(b'Computacao Grafica - Thomaz e Samuel')

    # Função responsável por fazer as inicializações
    init()

    # Registra a funcao callback de redesenho da janela de visualizacao
    glutDisplayFunc(desenha)

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)
    # Registra a função de callback para redimensionamento da janela
    
    glutIdleFunc(update_animation)

    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
