# OpenGL Camera & OBJ Viewer

좌표 변환, 카메라 조작과 OBJ 렌더링을 구현한 Python 그래픽스 실습입니다. NumPy, PyOpenGL, GLFW와 PyGLM을 사용합니다.

## 구현

- [main.py](main.py): model/view/projection 행렬, orbit·pan·zoom 카메라, grid
- [main1.py](main1.py): OBJ 정점·면 파싱, triangle fan 분할, 법선과 Phong 조명
- 주차별 폴더: 좌표 변환, 계층 변환, Euler 각과 회전 보간

카메라 상태는 Python에서, 정점 변환과 조명은 GLSL shader에서 처리합니다. Triangle fan은 복잡한 오목 다각형의 일반적인 분할을 지원하지 않습니다.

## 실행

OpenGL 3.3을 지원하는 GUI 환경이 필요합니다.

```bash
pip install numpy PyOpenGL glfw PyGLM
python main.py
python main1.py
```

OBJ 파일은 별도로 준비하며 키·마우스 동작은 각 프로그램의 callback에서 확인할 수 있습니다.

[구현 노트](docs/implementation.md) · [소스 목록](docs/source-index.csv) · [출처](ATTRIBUTION.md)
