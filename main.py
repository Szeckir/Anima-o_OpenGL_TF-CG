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
last_frame_time = 0.0  #seg ultimo frame
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
COEFICIENTE_QUIQUE = 0.6 #sobe

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
    global head_model, particles, last_frame_time, current_camera_position, current_camera_target
    
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

    last_frame_time = time.time() # Inicializa o tempo do último frame

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

        if particles:
            avg_x = sum(p.current_pos.x for p in particles) / len(particles)
            avg_y = sum(p.current_pos.y for p in particles) / len(particles)
            avg_z = sum(p.current_pos.z for p in particles) / len(particles)
            
            target_target = Ponto(avg_x, avg_y + camera_config["falling"]["target_offset_y"], avg_z)
            target_pos = Ponto(avg_x + camera_config["falling"]["pos_offset_x"], 
                                avg_y + camera_config["falling"]["pos_offset_y"], 
                                avg_z + camera_config["falling"]["pos_offset_z"])
        else: # Fallback if no particles (shouldn't happen after init)
            target_pos = camera_config["initial"]["pos"]
            target_target = camera_config["initial"]["target"]

    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO:
        # Fase 3: Redemoinho - Câmera vai para baixo e acompanha o tornado
        current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO)
        progress = current_phase_time / TEMPO_TORNADO_REFORMANDO

        # A câmera começa de baixo e sobe um pouco com o tornado
        target_pos_x = camera_config["tornado"]["pos"].x
        target_pos_y = camera_config["tornado"]["pos"].y + (progress * 5.0) # Sobe 5 unidades
        target_pos_z = camera_config["tornado"]["pos"].z

        target_target_y = camera_config["tornado"]["target"].y + (progress * 3.0) # Olha para cima
        
        target_pos = Ponto(target_pos_x, target_pos_y, target_pos_z)
        target_target = Ponto(camera_config["tornado"]["target"].x, target_target_y, camera_config["tornado"]["target"].z)

    elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA:
        # Fase 4: Cabeça formada - Câmera se aproxima do lado
        current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO)
        progress = min(1.0, current_phase_time / TEMPO_CABECA_FORMADA) # Garante que o progresso não exceda 1.0

        # Interpola da última posição para a posição final
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
        
        # Para suavizar a transição da câmera para a posição final
        # Usamos um lerp mais agressivo no início da fase final
        cam_interpolacao = 0.05 + (progress * 0.05) # Aumenta o fator de interpolação gradualmente
    else:
        # Fase 5: Extra - Efeito pulsar com rotação
        current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA)
        progress = min(1.0, current_phase_time / TEMPO_EFEITO_PULSAR)
        
        # Mova a câmera para a frente para ver a cabeça rotacionando
        target_pos = camera_config["extra"]["pos"]
        target_target = camera_config["extra"]["target"]
        
        # Transição suave da câmera
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

    # Interpolação suave para a posição e alvo da câmera
    current_camera_position.x = current_camera_position.x * (1 - cam_interpolacao) + target_pos.x * cam_interpolacao
    current_camera_position.y = current_camera_position.y * (1 - cam_interpolacao) + target_pos.y * cam_interpolacao
    current_camera_position.z = current_camera_position.z * (1 - cam_interpolacao) + target_pos.z * cam_interpolacao

    current_camera_target.x = current_camera_target.x * (1 - cam_interpolacao) + target_target.x * cam_interpolacao
    current_camera_target.y = current_camera_target.y * (1 - cam_interpolacao) + target_target.y * cam_interpolacao
    current_camera_target.z = current_camera_target.z * (1 - cam_interpolacao) + target_target.z * cam_interpolacao


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

def update_animation():
    """
    Função de atualização da lógica da animação. Chamada continuamente.
    """
    global animation_time, last_frame_time, animation_phase, is_playing

    current_time = time.time()
    dt = current_time - last_frame_time
    last_frame_time = current_time

    if is_playing:
        animation_time += dt * animation_speed

        # Lógica das fases da animação
        if animation_time < TEMPO_CABECA_DIZENDO_SIM:
            # Fase 1: Movimento de "sim" da cabeça
            pass # A rotação é aplicada no `desenha()` para o modelo completo.

        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO:
            # Fase 2: Desmontagem (partículas caem no chão e quicam)
            for p in particles:
                p.apply_force(FORCA_GRAVIDADE) # Aplica gravidade
                p.update(dt)

                # Colisão com o "chão" (y = -1, que é a posição do piso)
                if p.current_pos.y < -1.0:
                    p.current_pos.y = -1.0 # Para de cair no chão
                    p.velocity.y *= -COEFICIENTE_QUIQUE # Inverte a velocidade vertical e aplica o coeficiente de restituição
                    # Se a velocidade for muito baixa, para o quique
                    if abs(p.velocity.y) < 0.1:
                        p.velocity.y = 0.0
                    # Adiciona um pouco de atrito horizontal para as partículas pararem
                    p.velocity.x *= 0.95 # Reduz a velocidade horizontal
                    p.velocity.z *= 0.95 # Reduz a velocidade horizontal
        
        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO:
            # Fase de atraso após a queda, antes do redemoinho
            # As partículas permanecem paradas no chão
            for p in particles:
                p.velocity = Ponto(0,0,0)
                p.acceleration = Ponto(0,0,0)
            pass

        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO:
            # Fase 3: Redemoinho e formação da cabeça
            current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO)
            
            # Fator de progresso da fase de redemoinho (0 a 1)
            progress = current_phase_time / TEMPO_TORNADO_REFORMANDO

            # Ponto central do tornado que sobe
            tornado_center_y = -1.0 + (progress * 5.0) # Começa no chão e sobe
            tornado_center = Ponto(0, tornado_center_y, 0)

            for p in particles:
                # Vetor da partícula para o centro do tornado
                vec_to_center = tornado_center - p.current_pos
                
                # Força de atração principal (puxa para o centro do tornado)
                attraction_strength = 5.0 + (progress * 15.0) # Aumenta a força de atração
                attraction_force = vec_to_center.normalize() * attraction_strength

                # Força espiral (tangencial ao centro do tornado no plano XZ)
                # Quanto mais longe do centro, maior a força espiral
                distance_from_center_xz = Ponto(p.current_pos.x, 0, p.current_pos.z).length()
                
                spiral_strength = 10.0 * progress # Aumenta a força espiral com o progresso
                
                # Vetor perpendicular ao vetor do centro para a partícula no plano XZ
                # Isso cria a rotação
                spiral_direction = Ponto(-vec_to_center.z, 0, vec_to_center.x).normalize()
                spiral_force = spiral_direction * spiral_strength * distance_from_center_xz # Mais forte longe do centro
                
                # Força de elevação (para o tornado subir)
                upward_force_strength = 8.0 * progress # Força para cima, aumenta com o progresso
                upward_force = Ponto(0, upward_force_strength, 0)

                # Combina as forças
                total_force = attraction_force + spiral_force + upward_force
                p.apply_force(total_force)
                p.update(dt)

                # Se a partícula estiver muito próxima da posição original, "trava" ela
                if (p.current_pos - p.original_pos).length() < 0.1:
                    p.current_pos = p.original_pos.copy()
                    p.velocity = Ponto(0,0,0)
                    p.acceleration = Ponto(0,0,0)

        elif animation_time < TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA:
            # Fase 4: Cabeça formada
            for p in particles:
                p.current_pos = p.original_pos.copy()
                p.velocity = Ponto(0,0,0)
                p.acceleration = Ponto(0,0,0)
        else:
            # Fase 5: Extra - Efeito pulsar com rotação
            current_phase_time = animation_time - (TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO + TEMPO_CABECA_FORMADA)
            
            # Efeito de pulsação - Calcula um fator de expansão usando função seno
            # Oscila entre 0.95 e 1.05 (5% de expansão/contração)
            pulse_factor = 1.0 + 0.05 * math.sin(current_phase_time * 2 * math.pi)
            
            # Mudança gradual de cor com o tempo
            color_cycle = current_phase_time / 2.0  # Ciclo de cores a cada 2 segundos
            
            for p in particles:
                # Posição pulsante - expande e contrai a partir do centro
                center = Ponto(0, 0, 0)
                direction = p.original_pos - center
                p.current_pos = center + direction * pulse_factor
                
                # Mudança gradual de cor (efeito de onda de cores)
                r = 0.5 + 0.5 * math.sin(color_cycle * 2 * math.pi)
                g = 0.5 + 0.5 * math.sin(color_cycle * 2 * math.pi + 2 * math.pi/3)
                b = 0.5 + 0.5 * math.sin(color_cycle * 2 * math.pi + 4 * math.pi/3)
                p.color = [r, g, b]
                
                # Mantém velocidade e aceleração zeradas
                p.velocity = Ponto(0,0,0)
                p.acceleration = Ponto(0,0,0)


        # Garante que o tempo da animação não exceda o total
        if animation_time > TEMPO_TOTAL_ANIMACAO:
            animation_time = TEMPO_TOTAL_ANIMACAO
            is_playing = False # Pausa a animação no final

        

    glutPostRedisplay() # Solicita um redesenho da cena

def teclado(key, x, y):
    """
    Função de callback para tratamento de eventos de teclado.
    Controla a reprodução da animação (PLAY, PAUSE, REWIND, FORWARD).
    """
    global is_playing, animation_time, animation_speed, animation_phase, particles, current_camera_position, current_camera_target, camera_zoom, controlar_cam

    key = key.decode("utf-8").upper() # Converte a tecla para maiúscula

    if key == 'P': # Play/Pause
        is_playing = not is_playing
        print("play" if is_playing else "pausada")
    elif key == 'R': # Rewind (Voltar)
        animation_time = 0.0 # Reinicia a animação
        for p in particles: # Reseta todas as partículas para suas posições originais
            p.reset_position()
        # Resetar a posição da câmera para o início
        current_camera_position = camera_config["initial"]["pos"].copy()
        current_camera_target = camera_config["initial"]["target"].copy()
        print("reiniciada")
    elif key == 'F': # Forward (Avançar)
        # Avançar a animação de partículas é complexo, pois o estado depende do tempo.
        # Para simplificar, vamos pular para o final da fase de redemoinho.
        animation_time = TEMPO_CABECA_DIZENDO_SIM + TEMPO_CABECA_CAINDO + TEMPO_ESPERA_NO_CHAO + TEMPO_TORNADO_REFORMANDO # Pula para o início da fase final
        for p in particles: # Garante que as partículas estejam na posição original para a fase final
            p.reset_position()
        # Ajusta a câmera para a fase final
        current_camera_position = camera_config["final"]["pos"].copy()
        current_camera_target = camera_config["final"]["target"].copy()
        print("animacao avancada")
    elif key == 'W':  # Zoom in (aproximar)
        if animation_time >= TEMPO_TOTAL_ANIMACAO:  # Só funciona após o fim da animação
            camera_zoom -= 0.5  # Reduz a distância (aproxima)
            camera_zoom = max(2.0, camera_zoom)  # Limita o zoom mínimo
    elif key == 'S':  # Zoom out (afastar)
        if animation_time >= TEMPO_TOTAL_ANIMACAO:  # Só funciona após o fim da animação
            camera_zoom += 0.5  # Aumenta a distância (afasta)
            camera_zoom = min(20.0, camera_zoom)  # Limita o zoom máximo

    glutPostRedisplay() # Solicita um redesenho após a interação do teclado

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
