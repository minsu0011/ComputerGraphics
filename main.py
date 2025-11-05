from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

vertex_shader_src = '''
#version 330 core

layout(location = 0) in vec3 vin_pos;

uniform mat4 MVP;

void main() 
{
    gl_Position = MVP * vec4(vin_pos, 1.0);
}
'''

fragment_shader_src = '''
#version 330 core

out vec4 FragColor;

void main() 
{
    FragColor = vec4(0.6, 0.6, 0.6, 1.0);
}
'''

# Globals for camera state
camera = None
MODE_NONE, MODE_ORBIT, MODE_PAN, MODE_ZOOM = 0, 1, 2, 3
mode = MODE_NONE
last_x = last_y = 0
ORBIT_SENS, PAN_SENS, ZOOM_SENS = 0.005, 0.01, 0.1

def load_shaders(vertex_shader_source, fragment_shader_source):
    # build and compile our shader program
    # ------------------------------------
    
    # vertex shader 
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)    # create an empty shader object
    glShaderSource(vertex_shader, vertex_shader_source) # provide shader source code
    glCompileShader(vertex_shader)                      # compile the shader object
    
    # check for shader compile errors
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(vertex_shader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())
        
    # fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)    # create an empty shader object
    glShaderSource(fragment_shader, fragment_shader_source) # provide shader source code
    glCompileShader(fragment_shader)                        # compile the shader object
    
    # check for shader compile errors
    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(fragment_shader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

    # link shaders
    shader_program = glCreateProgram()               # create an empty program object
    glAttachShader(shader_program, vertex_shader)    # attach the shader objects to the program object
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)                    # link the program object

    # check for linking errors
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if (not success):
        infoLog = glGetProgramInfoLog(shader_program)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())
        
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program    # return the shader program

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



def draw_grid(vao, count, mvp_loc):
    glBindVertexArray(vao)
    glDrawArrays(GL_LINES, 0, count)



def main():
    if not glfwInit(): return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3); glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3)
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE)
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT,GL_TRUE)

    win = glfwCreateWindow(1600,1600,'2020017410 전민수',None,None)
    if not win: glfwTerminate(); return
    glfwMakeContextCurrent(win)
    glfwSetKeyCallback(win, key_callback)
    glfwSetCursorPosCallback(win, cursor_callback)
    glfwSetMouseButtonCallback(win, button_callback)
    glfwSetScrollCallback(win, scroll_callback)

    prog = load_shaders(vertex_shader_src, fragment_shader_src)
    mvp_loc = glGetUniformLocation(prog, 'MVP')
    vao_grid, grid_count = prepare_vao_grid(10,1.0)
    init_camera()

    while not glfwWindowShouldClose(win):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT); glEnable(GL_DEPTH_TEST)
        w,h = glfwGetFramebufferSize(win); glViewport(0,0,w,h)
        asp = w/float(h)
        P = glm.perspective(glm.radians(45.0), asp, 0.1, 100.0)
        V = glm.lookAt(camera['pos'], camera['target'], camera['cam_up'])

        glUseProgram(prog)
        MVP = P*V*glm.mat4(1.0)
        glUniformMatrix4fv(mvp_loc,1,GL_FALSE,glm.value_ptr(MVP))

        draw_grid(vao_grid, grid_count, mvp_loc)

        glfwSwapBuffers(win); glfwPollEvents()

    glfwTerminate()

if __name__=='__main__':
    main()
