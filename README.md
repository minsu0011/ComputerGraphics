# Interactive Computer Graphics
Python/OpenGL로 좌표 변환, 카메라 조작, 메쉬 렌더링을 학습한 실습 저장소입니다. 기존 과제별 코드와 커밋 이력을 유지합니다.

## 구현
`main.py`는 MVP 변환, grid VAO, orbit/pan/zoom 카메라를 구현합니다. `main1.py`는 OBJ 면의 삼각분할과 법선·Phong 조명을 포함하는 메쉬 렌더링 경로입니다. 주차별 코드에는 변환, 계층 애니메이션, Euler 각과 보간 실험이 분리돼 있습니다. 이 저장소를 범용 3D 엔진으로 설명하지 않습니다.

## 실행과 입력
Python, NumPy, PyOpenGL, glfw, PyGLM 및 OpenGL 3.3 가능한 화면 환경이 필요합니다. `python main.py`로 시작하고 메쉬 예제는 `python main1.py`를 사용합니다. OBJ 파일은 사용 권한이 있는 파일을 직접 준비하세요.

## 검증 및 한계
확인한 범위는는 Python 구문과 구현 경로를 검사합니다. 실제 GPU 화면·마우스 상호작용·드라이버별 렌더링을 자동 재현한 것은 아닙니다. OBJ triangulation은 복잡한 오목 polygon 전체에 대한 robust geometry solver가 아닙니다. 수업 starter와 학생 구현의 권리 경계가 확인되지 않아 private으로 관리합니다.

Canonical PC는 Laptop입니다. Desktop 복사본은 사용자가 제거했으므로 cross-device 검증은 NOT_REQUIRED입니다. [구현 안내](docs/implementation.md)를 참고하세요.
