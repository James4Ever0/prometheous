export HEADLESS=true

# # advice for rebuilding pyjom:
# # doing it step by step. 
# # cache steps.
# # doing small trials repeatedly, for a long time, for many many feedback loops.
# # then maybe someday it would go automatic.

bash build_gemini_doc.sh -s 
env PROJECT_NAME="graph-of-thoughts" AUTHOR="spcl" bash build_doc_with_author_and_project_name.sh -s
env PROJECT_NAME="LLM_Tree_Search" AUTHOR="waterhorse1" bash build_doc_with_author_and_project_name.sh -s
bash build_pyjom_doc.sh -s
env PROJECT_NAME="DALLE2-pytorch" AUTHOR="lucidrains" bash build_doc_with_author_and_project_name.sh -s
env PROJECT_NAME="Kacket" AUTHOR="ShorterThanDijkstra" bash build_doc_with_author_and_project_name.sh -s
env PROJECT_NAME="vced" AUTHOR="datawhalechina" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="he4o" AUTHOR="jiaxiaogang" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="gato" AUTHOR="OrigamiDream" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="Voyager" AUTHOR="MineDojo" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="RoboGen" AUTHOR="Genesis-Embodied-AI" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="mcts-for-llm" AUTHOR="shunzh" bash build_doc_at_prima_with_author_and_project_name.sh -s 

env PROJECT_NAME="lmql-tree-of-thoughts" AUTHOR="LachlanGray" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="RT-X" AUTHOR="kyegomez" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="tree-of-thoughts" AUTHOR="kyegomez" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="robotics_transformer" AUTHOR="google-research" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="q-transformer" AUTHOR="lucidrains" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="PaddleVideo" AUTHOR="PaddlePaddle" bash build_doc_at_prima_with_author_and_project_name.sh -s

# # note: for time we only do some documentation for some repo.

env PROJECT_NAME="robo_transformers" AUTHOR="sebbyjp" bash build_doc_at_prima_with_author_and_project_name.sh -s

# new
env PROJECT_NAME="DynamiCrafter" AUTHOR="Doubiiu" bash build_doc_at_prima_with_author_and_project_name.sh -s

env PROJECT_NAME="local_rag" AUTHOR="erenirmak" bash build_doc_at_prima_with_author_and_project_name.sh -s
# env PROJECT_NAME="RWKV-LM" AUTHOR="BlinkDL" bash build_doc_at_prima_with_author_and_project_name.sh -s

# new
env PROJECT_NAME="act-plus-plus" AUTHOR="MarkFzp" bash build_doc_at_prima_with_author_and_project_name.sh -s

env PROJECT_NAME="open_x_embodiment" AUTHOR="google-deepmind" bash build_doc_at_prima_with_author_and_project_name.sh -s

# new
env PROJECT_NAME="mobile-aloha" AUTHOR="MarkFzp" bash build_doc_at_prima_with_author_and_project_name.sh -s

env PROJECT_NAME="google-research" AUTHOR="google-research" bash build_doc_at_prima_with_author_and_project_name.sh -s

# new
env PROJECT_NAME="NExT-Chat" AUTHOR="NExT-ChatV" bash build_doc_at_prima_with_author_and_project_name.sh -s

env PROJECT_NAME="MultiModalMamba" AUTHOR="kyegomez" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="RT-2" AUTHOR="kyegomez" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="AutoRT" AUTHOR="kyegomez" bash build_doc_at_prima_with_author_and_project_name.sh -s
env PROJECT_NAME="autodoc" AUTHOR="context-labs" bash build_doc_at_prima_with_author_and_project_name.sh -s

# env PROJECT_NAME="llama_index" AUTHOR="run-llama" bash build_doc_at_prima_with_author_and_project_name.sh -s

# # do not do anything to gitee projects. ignore rules are not done yet.
