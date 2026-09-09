# Rendering path
main.py: CPU camera state → view/projection/model matrices → MVP uniform → vertex transform → fragment color. Mouse callbacks update orbit/pan/zoom; grid vertices are uploaded through VAO/VBO.
main1.py: OBJ faces → triangle fan → normals → lighting shader. A general polygon tessellator, material pipeline, physically based renderer는 구현했다고 주장하지 않습니다.
주차별 연습은 좌표계·계층 변환과 회전 보간을 비교합니다. Desktop source merge는 불필요합니다. 자동 검사는 Python syntax뿐이며 GPU interaction 검증은 별도입니다.

