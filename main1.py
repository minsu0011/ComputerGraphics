from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np
import os


vertex_grid_shader = '''
#version 330 core
layout(location = 0) in vec3 vin_pos;
uniform mat4 MVP;
void main() { gl_Position = MVP * vec4(vin_pos, 1.0); }
'''

fragment_grid_shader = '''
#version 330 core
out vec4 FragColor;
void main() { FragColor = vec4(0.6,0.6,0.6,1.0); }
'''

vertex_obj_shader = '''
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;
uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
uniform mat3 NormalMatrix;
out vec3 FragPos;
out vec3 Normal;
void main() {
    FragPos = vec3(M * vec4(aPos, 1.0));
    Normal = normalize(NormalMatrix * aNormal);
    gl_Position = P * V * vec4(FragPos, 1.0);
}
'''

fragment_obj_shader = '''
#version 330 core
in vec3 FragPos;
in vec3 Normal;
out vec4 FragColor;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor;
uniform float shininess;
void main() {
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    float specularStrength = 0.5;
    vec3 specular = specularStrength * spec * lightColor;
    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, 1.0);
}
'''

# Camera globals
camera = None
MODE_NONE, MODE_ORBIT, MODE_PAN, MODE_ZOOM = 0,1,2,3
mode = MODE_NONE 
last_x = last_y = 0
ORBIT_SENS, PAN_SENS, ZOOM_SENS = 0.005, 0.01, 0.1

def load_shaders(vertex_shader_source, fragment_shader_source):
    # build and compile our shader program
    # ------------------------------------
    # vertex shader
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    # check for shader compile errors
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if not success:
        infoLog = glGetShaderInfoLog(vertex_shader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())

    # fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # check for shader compile errors
    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if not success:
        infoLog = glGetShaderInfoLog(fragment_shader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

    # link shaders
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    # check for linking errors
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if not success:
        infoLog = glGetProgramInfoLog(shader_program)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program

def prepare_vao_grid(n=10, spacing=1.0):
    lines = []
    for i in range(-n, n+1):
        lines += [i*spacing, 0, -n*spacing,  i*spacing, 0, n*spacing]
        lines += [-n*spacing, 0, i*spacing,  n*spacing, 0, i*spacing]
    arr = np.array(lines, dtype=np.float32)
    vao = glGenVertexArrays(1); vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, arr.nbytes, arr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glBindVertexArray(0)
    return vao, len(arr)//3

def init_camera():
    global camera
    camera = {
        'target': glm.vec3(0,0,0),
        'dist': 5.0,
        'az': glm.radians(45.0),
        'el': glm.radians(30.0)
    }
    update_cam()


def update_cam():
    c = camera
    x = np.cos(c['el'])*np.sin(c['az'])
    y = np.sin(c['el'])
    z = np.cos(c['el'])*np.cos(c['az'])
    dir = glm.normalize(glm.vec3(x,y,z))
    c['pos'] = c['target'] + (-dir)*c['dist']
    c['up'] = glm.vec3(0,1,0)
    c['right'] = glm.normalize(glm.cross(c['up'], -dir))
    c['cam_up'] = glm.normalize(glm.cross(-dir, c['right']))



meshes = []

def triangulate(face):
    return [(face[0], face[i], face[i+1]) for i in range(1, len(face)-1)]


def load_obj(path, x_offset):
    verts, norms, faces = [], [], []
    with open(path) as f:
        for line in f:
            if line.startswith('v '): verts.append(list(map(float, line.split()[1:4])))
            elif line.startswith('vn '): norms.append(list(map(float, line.split()[1:4])))
            elif line.startswith('f '):
                parts = line.split()[1:]; idx = []
                for p in parts:
                    vi, *_ = p.split('/'); ni = p.split('/')[-1] if p.count('/')>=2 else None
                    idx.append((int(vi)-1, int(ni)-1 if ni else -1))
                faces.append(idx)
    total = len(faces); tri = len([f for f in faces if len(f)==3])
    quad = len([f for f in faces if len(f)==4]); ng = len([f for f in faces if len(f)>4])
    print(f"Loaded: {os.path.basename(path)} | total={total}, tri={tri}, quad={quad}, >4={ng}")
    v_arr, n_arr = [], []
    for f in faces:
        tris = [f] if len(f) == 3 else triangulate(f)
        for tri in tris:
            for vi, ni in tri:
                pos = verts[vi]
                norm = norms[ni] if ni >= 0 else [0, 0, 1]
                v_arr += [pos[0] + x_offset, pos[1], pos[2]]
                n_arr += norm
    v_arr = np.array(v_arr, dtype=np.float32); n_arr = np.array(n_arr, dtype=np.float32)
    vao = glGenVertexArrays(1); vbo = glGenBuffers(2)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0]); glBufferData(GL_ARRAY_BUFFER, v_arr.nbytes, v_arr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0); glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[1]); glBufferData(GL_ARRAY_BUFFER, n_arr.nbytes, n_arr, GL_STATIC_DRAW)
    glEnableVertexAttribArray(1); glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)
    glBindVertexArray(0)
    meshes.append({'vao': vao, 'count': len(v_arr)//3, 'offset': x_offset})


def key_callback(win, key, sc, act, mods):
    if key==GLFW_KEY_ESCAPE and act==GLFW_PRESS:
        glfwSetWindowShouldClose(win, GLFW_TRUE)

def cursor_callback(win, x, y):
    global last_x, last_y, mode
    if mode!=MODE_NONE:
        dx, dy = x-last_x, y-last_y
        if mode==MODE_ORBIT:
            camera['az'] += dx*ORBIT_SENS; camera['el'] += dy*ORBIT_SENS
        elif mode==MODE_PAN:
            camera['target'] += -camera['right']*dx*PAN_SENS + camera['cam_up']*dy*PAN_SENS
        elif mode==MODE_ZOOM:
            camera['dist'] += dy*ZOOM_SENS
            camera['dist']=max(0.1, camera['dist'])
        update_cam(); last_x, last_y = x, y

def button_callback(win, button, act, mods):
    global mode, last_x, last_y
    if button==GLFW_MOUSE_BUTTON_LEFT:
        if act==GLFW_PRESS:
            last_x, last_y = glfwGetCursorPos(win)
            if mods & GLFW_MOD_ALT:
                mode = MODE_ZOOM if mods&GLFW_MOD_CONTROL else MODE_PAN if mods&GLFW_MOD_SHIFT else MODE_ORBIT
        else:
            mode = MODE_NONE

def scroll_callback(win, xo, yo):
    camera['dist'] += -yo*ZOOM_SENS; camera['dist']=max(0.1, camera['dist']); update_cam()

def drop_callback(win, paths):
    count = len(meshes)
    for p in paths:
        if p.lower().endswith('.obj'):
            load_obj(p, count*2.0); count+=1


def draw_grid(vao, cnt, shader, mvp_loc, P, V):
    glUseProgram(shader)
    MVP = P * V * glm.mat4(1.0)
    glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, glm.value_ptr(MVP))
    glBindVertexArray(vao)
    glDrawArrays(GL_LINES, 0, cnt)

def draw_meshes(prog):
    glUseProgram(prog)

    glUniform3fv(glGetUniformLocation(prog,'lightPos'),1,glm.value_ptr(glm.vec3(5,5,5)))
    glUniform3fv(glGetUniformLocation(prog,'viewPos'),1,glm.value_ptr(camera['pos']))
    glUniform3fv(glGetUniformLocation(prog,'lightColor'),1,glm.value_ptr(glm.vec3(1,1,1)))
    glUniform3fv(glGetUniformLocation(prog,'objectColor'),1,glm.value_ptr(glm.vec3(0.8,0.5,0.3)))
    glUniform1f(glGetUniformLocation(prog,'shininess'),32.0)

    for m in meshes:
        M = glm.translate(glm.mat4(1.0), glm.vec3(m['offset'],0,0))
        NormalMatrix = glm.mat3(glm.transpose(glm.inverse(M)))
        glUniformMatrix4fv(glGetUniformLocation(prog,'M'),1,GL_FALSE,glm.value_ptr(M))
        glUniformMatrix4fv(glGetUniformLocation(prog,'V'),1,GL_FALSE,glm.value_ptr(V))
        glUniformMatrix4fv(glGetUniformLocation(prog,'P'),1,GL_FALSE,glm.value_ptr(P))
        glUniformMatrix3fv(glGetUniformLocation(prog,'NormalMatrix'),1,GL_FALSE,glm.value_ptr(NormalMatrix))
        glBindVertexArray(m['vao']); glDrawArrays(GL_TRIANGLES,0,m['count'])

if __name__=='__main__':
    if not glfwInit(): exit()
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3); glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3)
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE)
    win = glfwCreateWindow(1600,1600,'2020017410',None,None)
    if not win: glfwTerminate(); exit()
    glfwMakeContextCurrent(win)
    glfwSetKeyCallback(win, key_callback)
    glfwSetCursorPosCallback(win, cursor_callback)
    glfwSetMouseButtonCallback(win, button_callback)
    glfwSetScrollCallback(win, scroll_callback)
    glfwSetDropCallback(win, drop_callback)

    grid_prog = load_shaders(vertex_grid_shader, fragment_grid_shader)
    obj_prog = load_shaders(vertex_obj_shader, fragment_obj_shader)
    vao_grid, grid_cnt = prepare_vao_grid(10,1.0)
    mvp_loc = glGetUniformLocation(grid_prog,'MVP')
    init_camera()

    while not glfwWindowShouldClose(win):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT); glEnable(GL_DEPTH_TEST)
        w,h = glfwGetFramebufferSize(win); glViewport(0,0,w,h)
        asp = w/float(h)
        P = glm.perspective(glm.radians(45.0), asp, 0.1, 100.0)
        V = glm.lookAt(camera['pos'], camera['target'], camera['cam_up'])
        # draw grid & meshes
        draw_grid(vao_grid, grid_cnt, grid_prog, mvp_loc, P, V)
        draw_meshes(obj_prog)
        glfwSwapBuffers(win); glfwPollEvents()
    glfwTerminate()