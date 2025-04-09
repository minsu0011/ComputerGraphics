#1
'''
import glm
I = glm.array(glm.mat4())
print(I)
'''
#2
'''
import glm
m33 = glm.mat3(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)

a = m33[2];

v4 = glm.vec4((1.0, 2.0, 3.0, 4.0));
b = v4.xxy;

result = a*b;
print(result)
'''
#3
import glm
